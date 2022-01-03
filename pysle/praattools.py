# encoding: utf-8
"""Various utilities for using the ISLE dictionary with praat textgrids"""

from typing import List, Optional
from typing_extensions import Literal

from praatio import textgrid
from praatio import praatio_scripts
from praatio.utilities import constants as praatioConstants

from pysle import isletool
from pysle import phonetics
from pysle.utilities import errors
from pysle.utilities import constants
from pysle.utilities import utils
from pysle.utilities import phonetic_constants


def spellCheckTextgrid(
    tg: textgrid.Textgrid,
    tierName: str,
    annotationTierName: str,
    isle: isletool.Isle,
    printEntries: bool = False,
) -> textgrid.Textgrid:
    """Spell check words by using the praatio spellcheck function

    Incorrect items are noted in a new tier and optionally
        printed to the screen

    Args:
        tg: the textgrid to spellcheck
        tierName: the name of the tier to spellcheck
        annotationTierName: the name of the tier to create and write segments to
        isle: an instance of Isle
        printEntries: if True, words not in the dictionary will be printed
            to the screen

    Returns:
        a modified version of the input textgrid with a new tier marking all
        words that were not in the dictionary (presumably mispelled)
    """

    def checkFunc(word: str):
        return isle.contains(word)

    tg = praatio_scripts.spellCheckEntries(
        tg, tierName, annotationTierName, checkFunc, printEntries
    )

    return tg


def naiveWordAlignment(
    tg: textgrid.Textgrid,
    utteranceTierName: str,
    wordTierName: str,
    isle: isletool.Isle,
    phoneHelperTierName: Optional[str] = None,
    removeOverlappingSegments: bool = False,
) -> textgrid.Textgrid:
    """Performs naive alignment for utterances in a textgrid

    Naive alignment gives each segment equal duration.  Word duration is
    determined by the duration of an utterance and the number of phones in
    the word.

    By 'utterance' I mean a string of words separated by a space bounded
    in time eg (0.5, 1.5, "he said he likes ketchup").

    Args:
        tg: the textgrid to do alignment over
        utteranceTierName: name of the utterance tier to examine
        wordTierName: name of the word tier to create and write segments to
        isle: an instance of Isle
        phoneHelperTierName: creates a tier that is parallel to the word tier.
            However, the labels are the phones for the word, rather than the word
        removeOverlappingSegments: remove any labeled words or phones that
            fall under labeled utterances

    Returns:
        a modified version of the input textgrid with the word segmented

    Raises:
        WordNotInIsleError: The word was not in the Isle dictionary
    """
    utteranceTier = tg.tierDict[utteranceTierName]

    wordTier = None
    if wordTierName in tg.tierNameList:
        wordTier = tg.tierDict[wordTierName]

    # Load in the word tier, if it exists:
    wordEntryList = []
    phoneEntryList = []
    if wordTier is not None:
        if removeOverlappingSegments:
            for start, stop, _ in utteranceTier.entryList:
                wordTier = wordTier.eraseRegion(
                    start, stop, praatioConstants.EraseCollision.TRUNCATE, False
                )
        wordEntryList = wordTier.entryList

    # Do the naive alignment
    for start, stop, label in utteranceTier.entryList:
        wordList = label.split()

        # Get the list of phones in each word
        superPhoneList: List[List[str]] = []
        numPhones = 0
        i = 0
        while i < len(wordList):
            word = wordList[i]
            try:
                entry = isle.lookup(word)[0]
            except errors.WordNotInIsleError:
                wordList.pop(i)
                continue
            superPhoneList.append(entry.phonemeList.phonemes)
            numPhones += len(entry.phonemeList.phonemes)
            i += 1

        # Get the naive alignment for words, if alignment doesn't
        # already exist for words
        subWordEntryList = []
        subPhoneEntryList = []
        if wordTier is not None:
            subWordEntryList = wordTier.crop(
                start, stop, praatioConstants.CropCollision.TRUNCATED, False
            ).entryList

        if len(subWordEntryList) == 0:
            wordStart = start
            phoneDur = (stop - start) / float(numPhones)
            for i, word in enumerate(wordList):
                phoneListTxt = " ".join(superPhoneList[i])
                wordEnd = wordStart + (phoneDur * len(superPhoneList[i]))
                subWordEntryList.append((wordStart, wordEnd, word))
                subPhoneEntryList.append((wordStart, wordEnd, phoneListTxt))
                wordStart = wordEnd

        wordEntryList.extend(subWordEntryList)
        phoneEntryList.extend(subPhoneEntryList)

    # Replace or add the word tier
    newWordTier = textgrid.IntervalTier(
        wordTierName, wordEntryList, tg.minTimestamp, tg.maxTimestamp
    )
    if wordTier is not None:
        tg.replaceTier(wordTierName, newWordTier)
    else:
        tg.addTier(newWordTier)

    # Add the phone tier
    # This is mainly used as an annotation tier
    if phoneHelperTierName is not None and len(phoneEntryList) > 0:
        newPhoneTier = textgrid.IntervalTier(
            phoneHelperTierName, phoneEntryList, tg.minTimestamp, tg.maxTimestamp
        )
        if phoneHelperTierName in tg.tierNameList:
            tg.replaceTier(phoneHelperTierName, newPhoneTier)
        else:
            tg.addTier(newPhoneTier)

    return tg


def naivePhoneAlignment(
    tg: textgrid.Textgrid,
    wordTierName: str,
    phoneTierName: str,
    isle: isletool.Isle,
    removeOverlappingSegments: bool = False,
) -> textgrid.Textgrid:
    """Performs naive alignment for words in a textgrid

    Naive alignment gives each segment equal duration.
    Phone duration is determined by the duration of the word
    and the number of phones.

    Args:
        tg: the textgrid to do alignment over
        wordTierName: name of the utterance tier to examine
        phoneTierName: name of the word tier to create and write segments to
        isle: an instance of Isle
        removeOverlappingSegments: remove any labeled words or phones that
            fall under labeled utterances

    Returns:
        a modified version of the input textgrid with the word segmented

    Raises:
        WordNotInIsleError: The word was not in the Isle dictionary
    """
    wordTier = tg.tierDict[wordTierName]

    phoneTier = None
    if phoneTierName in tg.tierNameList:
        phoneTier = tg.tierDict[phoneTierName]

    # Load in the phone tier, if it exists:
    phoneEntryList = []
    if phoneTier is not None:
        if removeOverlappingSegments:
            for startT, stopT, _ in wordTier.entryList:
                phoneTier = phoneTier.eraseRegion(
                    startT, stopT, praatioConstants.EraseCollision.TRUNCATE, False
                )
        phoneEntryList = phoneTier.entryList

    # Do the naive alignment
    for wordStartT, wordEndT, word in wordTier.entryList:

        # Get the list of phones in this word
        try:
            entry = isle.lookup(word)[0]
        except errors.WordNotInIsleError:
            continue

        phones = entry.phonemeList.stripDiacritics().phonemes

        # Get the naive alignment for phones, if alignment doesn't
        # already exist for phones
        subPhoneEntryList = []
        if phoneTier is not None:
            subPhoneEntryList = phoneTier.crop(
                wordStartT, wordEndT, praatioConstants.CropCollision.TRUNCATED, False
            ).entryList

        if len(subPhoneEntryList) == 0:
            phoneDur = (wordEndT - wordStartT) / len(phones)

            phoneStartT = wordStartT
            for phone in phones:
                phoneEndT = phoneStartT + phoneDur
                subPhoneEntryList.append((phoneStartT, phoneEndT, phone))
                phoneStartT = phoneEndT

        phoneEntryList.extend(subPhoneEntryList)

    # Replace or add the phone tier
    newPhoneTier = textgrid.IntervalTier(
        phoneTierName, phoneEntryList, tg.minTimestamp, tg.maxTimestamp
    )
    if phoneTier is not None:
        tg.replaceTier(phoneTierName, newPhoneTier)
    else:

        tg.addTier(newPhoneTier)

    return tg


def syllabifyTextgrid(
    isle: isletool.Isle,
    tg: textgrid.Textgrid,
    wordTierName: str,
    phoneTierName: str,
    skipLabelList: Optional[List[str]] = None,
    start: Optional[float] = None,
    stop: Optional[float] = None,
    stressDetectionErrorMode: Literal["silence", "warning", "error"] = "error",
    syllabificationErrorMode: Literal["silence", "warning", "error"] = "error",
) -> textgrid.Textgrid:
    """Given a textgrid, syllabifies the phones in the textgrid

    The textgrid must have a word tier (used to lookup words) and a phone tier
    (for syllabifying).

    Args:
        isle: an instance of Isle
        tg: the textgrid to syllabify
        wordTierName: the tier containing intervals with one word per interval
        phoneTierName: tier containing intervals with one phone per interval
        skipLabelList: intervals in the word tier containing a label in this list
            will be skipped
        start: if not None, only consider intervals that appear after the start time
        stop: if not None, only consider intervals that appear before the stop time
        stressDetectionErrorMode: determines behavior if stress is not detected for
            a word
        syllabificationErrorMode: determines behavior if a word cannot be syllabified

    Returns:
        a textgrid with only two tiers containing syllable information
        (syllabification of the phone tier and a tier marking word-stress).

    Raises:
        WordNotInIsleError: the word was not in the dictionary
        StressedSyllableDetectionError: no stress found for a word
    """
    utils.validateOption(
        "stressDetectionErrorMode",
        stressDetectionErrorMode,
        constants.ErrorReportingMode,
    )

    utils.validateOption(
        "syllabificationErrorMode",
        syllabificationErrorMode,
        constants.ErrorReportingMode,
    )

    stressErrorReporter = utils.getErrorReporter(stressDetectionErrorMode)
    syllabificationErrorReporter = utils.getErrorReporter(syllabificationErrorMode)

    minT = tg.minTimestamp
    maxT = tg.maxTimestamp

    wordTier = tg.tierDict[wordTierName]
    phoneTier = tg.tierDict[phoneTierName]

    if not isinstance(wordTier, textgrid.IntervalTier):
        raise AttributeError(f"Tier '{wordTierName}' must be an interval tier")
    if not isinstance(phoneTier, textgrid.IntervalTier):
        raise AttributeError(f"Tier '{phoneTierName}' must be an interval tier")

    if skipLabelList is None:
        skipLabelList = []

    syllableEntryList = []
    tonicSEntryList = []
    tonicPEntryList = []

    if start is not None or stop is not None:
        if start is None:
            start = minT
        if stop is None:
            stop = maxT

        wordTier = wordTier.crop(
            start, stop, praatioConstants.CropCollision.TRUNCATED, False
        )

    for entryStart, entryStop, word in wordTier.entryList:

        if word in skipLabelList:
            continue

        subPhoneTier = phoneTier.crop(
            entryStart, entryStop, praatioConstants.CropCollision.STRICT, False
        )

        phoneList = [entry[2] for entry in subPhoneTier.entryList if entry[2] != ""]

        try:
            sylTmp = isle.findBestSyllabification(word, phoneList)
        except errors.WordNotInIsleError:
            print(
                f"Not is isle -- skipping syllabification; Word '{word}' at {entryStart:.2f}"
            )
            continue
        except errors.NullPronunciationError:
            print(f"No provided pronunciation; Word '{word}' at {entryStart:.2f}")
            continue
        except errors.ImpossibleSyllabificationError as e:
            syllabificationErrorReporter(
                errors.ImpossibleSyllabificationError,
                f"Syllabification error; Word '{word}' at {entryStart:.2f}; " + str(e),
            )
            continue

        stressI = sylTmp.stressedVowelIndicies
        stressJ = sylTmp.stressedSyllableIndicies
        syllableList = sylTmp.syllables
        islesAdjustedSyllableList = syllableList

        if len(stressI) > 0 and len(stressJ) > 0:
            syllableList[stressI[0]].phonemes[stressJ[0]] += "ˈ"

        i = 0
        for k, syllable in enumerate(syllableList):

            # Create the syllable tier entry
            j = len(syllable)
            stubEntryList = subPhoneTier.entryList[i : i + j]
            i += j

            # The whole syllable was deleted
            if len(stubEntryList) == 0:
                continue

            syllableStart = stubEntryList[0][0]
            syllableEnd = stubEntryList[-1][1]
            label = "-".join([entry[2] for entry in stubEntryList])

            syllableEntryList.append((syllableStart, syllableEnd, label))

            # Create the tonic syllable tier entry
            if k == stressI:
                tonicSEntryList.append(
                    (syllableStart, syllableEnd, phonetic_constants.TONIC)
                )

            # Create the tonic phone tier entry
            if k == stressI:
                syllablePhoneTier = phoneTier.crop(
                    syllableStart,
                    syllableEnd,
                    praatioConstants.CropCollision.STRICT,
                    False,
                )

                tonicSyllableEntries: List[textgrid.constants.Interval] = [
                    entry for entry in syllablePhoneTier.entryList if entry[2] != ""
                ]
                tonicSyllable = phonetics.Syllable(
                    [phone for _, _, phone in tonicSyllableEntries]
                )
                cvList = tonicSyllable.simplify().phonemes

                tmpStressJ = None
                try:
                    tmpStressJ = cvList.index(phonetic_constants.VOWEL)
                except ValueError:
                    for char in phonetic_constants.STRESS_BEARING_CONSONANTS:
                        if char in cvList:
                            tmpStressJ = cvList.index(char)
                            break

                if tmpStressJ is None:
                    stressErrorReporter(
                        errors.StressedSyllableDetectionError,
                        f"No stressed syllable; word: '{word}' at {syllableStart:.2f}, "
                        f"actual mapped pronunciation: {syllableList}, "
                        f"ISLE's mapped pronunciation: {islesAdjustedSyllableList}",
                    )
                    continue

                phoneStart, phoneEnd = tonicSyllableEntries[tmpStressJ][:2]
                tonicPEntryList.append((phoneStart, phoneEnd, phonetic_constants.TONIC))

    # Create a textgrid with the two syllable-level tiers
    syllableTier = textgrid.IntervalTier("syllable", syllableEntryList, minT, maxT)
    tonicSTier = textgrid.IntervalTier("tonicSyllable", tonicSEntryList, minT, maxT)
    tonicPTier = textgrid.IntervalTier("tonicVowel", tonicPEntryList, minT, maxT)

    syllableTG = textgrid.Textgrid()
    syllableTG.addTier(syllableTier)
    syllableTG.addTier(tonicSTier)
    syllableTG.addTier(tonicPTier)

    return syllableTG
