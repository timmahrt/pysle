# encoding: utf-8
"""
Various utilities for using the ISLE dictionary with praat textgrids

see
**examples/alignment_example.py**
**examples/syllabify_textgrid.py**
"""

from typing import List, Optional
from typing_extensions import Literal

from pysle import pronunciationtools
from pysle import isle
from pysle.utilities import errors
from pysle.utilities import constants
from pysle.utilities import utils

try:
    from praatio import textgrid
    from praatio import praatio_scripts
    from praatio.utilities import constants as praatioConstants
except ImportError:
    raise errors.OptionalFeatureError()

STRESS_BEARING_CONSONANTS = ["r", "m", "n", "l"]
TONIC = "T"
VOWEL = "V"


def spellCheckTextgrid(
    tg: textgrid.Textgrid,
    targetTierName: str,
    newTierName: str,
    isleDict: isle.Isle,
    printEntries: bool = False,
) -> textgrid.Textgrid:
    """
    Spell check words by using the praatio spellcheck function

    Incorrect items are noted in a new tier and optionally
        printed to the screen
    """

    def checkFunc(word: str):
        try:
            isleDict.lookup(word)
        except errors.WordNotInISLE:
            returnVal = False
        else:
            returnVal = True

        return returnVal

    tg = praatio_scripts.spellCheckEntries(
        tg, targetTierName, newTierName, checkFunc, printEntries
    )

    return tg


def naiveWordAlignment(
    tg: textgrid.Textgrid,
    utteranceTierName: str,
    wordTierName: str,
    isleDict: isle.Isle,
    phoneHelperTierName: Optional[str] = None,
    removeOverlappingSegments: bool = False,
):
    """
    Performs naive alignment for utterances in a textgrid

    Naive alignment gives each segment equal duration.  Word duration is
    determined by the duration of an utterance and the number of phones in
    the word.

    By 'utterance' I mean a string of words separated by a space bounded
    in time eg (0.5, 1.5, "he said he likes ketchup").

    phoneHelperTierName - creates a tier that is parallel to the word tier.
                          However, the labels are the phones for the word,
                          rather than the word
    removeOverlappingSegments - remove any labeled words or phones that
                                fall under labeled utterances
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
            for startT, stopT, _ in utteranceTier.entryList:
                wordTier = wordTier.eraseRegion(
                    startT, stopT, praatioConstants.EraseCollision.TRUNCATE, False
                )
        wordEntryList = wordTier.entryList

    # Do the naive alignment
    for startT, stopT, label in utteranceTier.entryList:
        wordList = label.split()

        # Get the list of phones in each word
        superPhoneList = []
        numPhones = 0
        i = 0
        while i < len(wordList):
            word = wordList[i]
            try:
                firstSyllableList = isleDict.lookup(word)[0][0][0]
            except errors.WordNotInISLE:
                wordList.pop(i)
                continue
            phoneList = [phone for syllable in firstSyllableList for phone in syllable]
            superPhoneList.append(phoneList)
            numPhones += len(phoneList)
            i += 1

        # Get the naive alignment for words, if alignment doesn't
        # already exist for words
        subWordEntryList = []
        subPhoneEntryList = []
        if wordTier is not None:
            subWordEntryList = wordTier.crop(
                startT, stopT, praatioConstants.CropCollision.TRUNCATED, False
            ).entryList

        if len(subWordEntryList) == 0:
            wordStartT = startT
            phoneDur = (stopT - startT) / float(numPhones)
            for i, word in enumerate(wordList):
                phoneListTxt = " ".join(superPhoneList[i])
                wordEndT = wordStartT + (phoneDur * len(superPhoneList[i]))
                subWordEntryList.append((wordStartT, wordEndT, word))
                subPhoneEntryList.append((wordStartT, wordEndT, phoneListTxt))
                wordStartT = wordEndT

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
    isleDict: isle.Isle,
    removeOverlappingSegments: bool = False,
):
    """
    Performs naive alignment for words in a textgrid

    Naive alignment gives each segment equal duration.
    Phone duration is determined by the duration of the word
    and the number of phones.

    removeOverlappingSegments - remove any labeled words or phones that
                                fall under labeled utterances
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
            firstSyllableList = isleDict.lookup(word)[0][0][0]
        except errors.WordNotInISLE:
            continue

        phoneList = [phone for syllable in firstSyllableList for phone in syllable]
        for char in ["ˈ", "ˌ"]:
            phoneList = [phone.replace(char, "") for phone in phoneList]

        # Get the naive alignment for phones, if alignment doesn't
        # already exist for phones
        subPhoneEntryList = []
        if phoneTier is not None:
            subPhoneEntryList = phoneTier.crop(
                wordStartT, wordEndT, praatioConstants.CropCollision.TRUNCATED, False
            ).entryList

        if len(subPhoneEntryList) == 0:
            phoneDur = (wordEndT - wordStartT) / len(phoneList)

            phoneStartT = wordStartT
            for phone in phoneList:
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
    isleDict: isle.Isle,
    tg: textgrid.Textgrid,
    wordTierName: str,
    phoneTierName: str,
    skipLabelList: Optional[List[str]] = None,
    startT: Optional[float] = None,
    stopT: Optional[float] = None,
    stressDetectionErrorMode: Literal["ignore", "warn", "error"] = "error",
    syllabificationErrorMode: Literal["ignore", "warn", "error"] = "error",
):
    """
    Given a textgrid, syllabifies the phones in the textgrid

    skipLabelList allows you to skip labels without generating warnings
    (e.g. '', 'sp', etc.)

    The textgrid must have a word tier and a phone tier.

    Returns a textgrid with only two tiers containing syllable information
    (syllabification of the phone tier and a tier marking word-stress).
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

    minT = tg.minTimestamp
    maxT = tg.maxTimestamp

    wordTier = tg.tierDict[wordTierName]
    phoneTier = tg.tierDict[phoneTierName]

    if skipLabelList is None:
        skipLabelList = []

    syllableEntryList = []
    tonicSEntryList = []
    tonicPEntryList = []

    if startT is not None or stopT is not None:
        if startT is None:
            startT = minT
        if stopT is None:
            stopT = maxT

        wordTier = wordTier.crop(
            startT, stopT, praatioConstants.CropCollision.TRUNCATED, False
        )

    for start, stop, word in wordTier.entryList:

        if word in skipLabelList:
            continue

        subPhoneTier = phoneTier.crop(
            start, stop, praatioConstants.CropCollision.STRICT, False
        )

        phoneList = [entry[2] for entry in subPhoneTier.entryList if entry[2] != ""]

        try:
            sylTmp = pronunciationtools.findBestSyllabification(
                isleDict, word, phoneList
            )
        except errors.WordNotInISLE:
            print(
                f"Not is isle -- skipping syllabification; Word '{word}' at {start:.2f}"
            )
            continue
        except errors.NullPronunciationError:
            print(f"No provided pronunciation; Word '{word}' at {start:.2f}")
            continue
        except errors.ImpossibleSyllabificationError as e:
            if syllabificationErrorMode == constants.ErrorReportingMode.SILENCE:
                continue

            if syllabificationErrorMode == constants.ErrorReportingMode.WARNING:
                print(f"Syllabification error; Word '{word}' at {start:.2f}; " + str(e))
                continue

            raise

        stressI = sylTmp[0]
        stressJ = sylTmp[1]
        syllableList = sylTmp[2]
        islesAdjustedSyllableList = sylTmp[3]

        if stressI is not None and stressJ is not None:
            syllableList[stressI][stressJ] += "ˈ"

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
                tonicSEntryList.append((syllableStart, syllableEnd, TONIC))

            # Create the tonic phone tier entry
            if k == stressI:
                syllablePhoneTier = phoneTier.crop(
                    syllableStart,
                    syllableEnd,
                    praatioConstants.CropCollision.STRICT,
                    False,
                )

                syllablePhoneList = [
                    entry for entry in syllablePhoneTier.entryList if entry[2] != ""
                ]
                justPhones = [phone for _, _, phone in syllablePhoneList]
                cvList = pronunciationtools.simplifyPronunciation(justPhones)

                tmpStressJ = None
                try:
                    tmpStressJ = cvList.index(VOWEL)
                except ValueError:
                    for char in STRESS_BEARING_CONSONANTS:
                        if char in cvList:
                            tmpStressJ = cvList.index(char)
                            break

                if tmpStressJ is None:
                    if stressDetectionErrorMode == constants.ErrorReportingMode.SILENCE:
                        continue

                    if stressDetectionErrorMode == constants.ErrorReportingMode.WARNING:
                        print(
                            f"No stressed syllable; word: '{word}' at {syllableStart:.2f}, "
                            f"actual mapped pronunciation: {syllableList}, "
                            f"ISLE's mapped pronunciation: {islesAdjustedSyllableList}"
                        )
                        continue

                    raise (
                        errors.StressedSyllableDetectionError(
                            word, phoneList, syllableList, islesAdjustedSyllableList
                        )
                    )

                phoneStart, phoneEnd = syllablePhoneList[tmpStressJ][:2]
                tonicPEntryList.append((phoneStart, phoneEnd, TONIC))

    # Create a textgrid with the two syllable-level tiers
    syllableTier = textgrid.IntervalTier("syllable", syllableEntryList, minT, maxT)
    tonicSTier = textgrid.IntervalTier("tonicSyllable", tonicSEntryList, minT, maxT)
    tonicPTier = textgrid.IntervalTier("tonicVowel", tonicPEntryList, minT, maxT)

    syllableTG = textgrid.Textgrid()
    syllableTG.addTier(syllableTier)
    syllableTG.addTier(tonicSTier)
    syllableTG.addTier(tonicPTier)

    return syllableTG
