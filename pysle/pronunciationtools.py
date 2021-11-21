# encoding: utf-8
"""
Code for comparing and aligning pronunciation data with pronunciations found in the ISLE dictionary.

see **examples/pronunciationtools_examples.py**
"""

import itertools
import copy
from pkg_resources import resource_filename
from typing import List, Optional, Dict, Tuple, Union

from pysle import isle
from pysle.utilities import errors
from pysle.utilities import constants
from pysle.utilities import phonetic_constants


# The LCS code doesn't look like the rest of the code
# -- I'm guessing I copied or adapted the code from
#    someplace online
def _lcs_lens(xs: list, ys: list) -> list:
    curr = list(itertools.repeat(0, 1 + len(ys)))
    for x in xs:
        prev = list(curr)
        for i, y in enumerate(ys):
            if x == y:
                curr[i + 1] = prev[i] + 1
            else:
                curr[i + 1] = max(curr[i], prev[i + 1])
    return curr


def _lcs(xs: list, ys: list) -> list:
    nx, ny = len(xs), len(ys)
    if nx == 0:
        return []

    if nx == 1:
        return [xs[0]] if xs[0] in ys else []

    i = nx // 2
    xb, xe = xs[:i], xs[i:]
    ll_b = _lcs_lens(xb, ys)
    ll_e = _lcs_lens(xe[::-1], ys[::-1])
    _, k = max((ll_b[j] + ll_e[ny - j], j) for j in range(ny + 1))
    yb, ye = ys[:k], ys[k:]
    return _lcs(xb, yb) + _lcs(xe, ye)


def simplifyPronunciation(phoneList: List[str]) -> List[str]:
    pass


def _adjustSyllabification(adjustedPhoneList: List[str], syllableList: List[List[str]]):
    """
    Inserts spaces into a syllable if needed

    Originally the phone list and syllable list contained the same number
    of phones.  But the adjustedPhoneList may have some insertions which are
    not accounted for in the syllableList.
    """
    i = 0
    retSyllableList = []
    for syllableNum, syllable in enumerate(syllableList):
        j = len(syllable)
        if syllableNum == len(syllableList) - 1:
            j = len(adjustedPhoneList) - i
        tmpPhoneList = adjustedPhoneList[i : i + j]
        numBlanks = -1
        phoneList = tmpPhoneList[:]
        while numBlanks != 0:

            numBlanks = tmpPhoneList.count("''")
            if numBlanks > 0:
                tmpPhoneList = adjustedPhoneList[i + j : i + j + numBlanks]
                phoneList.extend(tmpPhoneList)
                j += numBlanks

        for k, phone in enumerate(phoneList):
            if phone == "''":
                syllable.insert(k, "''")

        i += j

        retSyllableList.append(syllable)

    return retSyllableList


def _findBestPronunciation(isleWordList: List[List[str]], aPron: List[str]):
    """
    Words may have multiple candidates in ISLE; returns the 'optimal' one.
    """

    aP = simplifyPronunciation(aPron)  # Mapping to simplified phone inventory

    numDiffList = []
    withStress = []
    i = 0
    alignedSyllabificationList = []
    alignedActualPronunciationList = []
    for wordTuple in isleWordList:
        aPronMap = copy.deepcopy(aPron)
        syllableList = wordTuple[0]  # syllableList, stressList

        iP = [phone for phoneList in syllableList for phone in phoneList]
        iP = simplifyPronunciation(iP)

        alignedIP, alignedAP = alignPronunciations(iP, aP)

        # Remapping to actual phones
        #         alignedAP = [origPronDict.get(phon, u"''") for phon in alignedAP]
        alignedAP = [aPronMap.pop(0) if phon != "''" else "''" for phon in alignedAP]
        alignedActualPronunciationList.append(alignedAP)

        # Adjusting the syllabification for differences between the dictionary
        # pronunciation and the actual pronunciation
        alignedSyllabification = _adjustSyllabification(alignedIP, syllableList)
        alignedSyllabificationList.append(alignedSyllabification)

        # Count the number of misalignments between the two
        numDiff = alignedIP.count("''") + alignedAP.count("''")
        numDiffList.append(numDiff)

        # Is there stress in this word
        hasStress = False
        for syllable in syllableList:
            for phone in syllable:
                hasStress = "ˈ" in phone or hasStress

        if hasStress:
            withStress.append(i)
        i += 1

    # Return the pronunciation that had the fewest differences
    #     to the actual pronunciation
    minDiff = min(numDiffList)

    # When there are multiple candidates that have the minimum number
    #     of differences, prefer one that has stress in it
    bestIndex = None
    bestIsStressed = None
    for i, numDiff in enumerate(numDiffList):
        if numDiff != minDiff:
            continue
        if bestIndex is None:
            bestIndex = i
            bestIsStressed = i in withStress
        else:
            if not bestIsStressed and i in withStress:
                bestIndex = i
                bestIsStressed = True

    return (
        isleWordList,
        alignedActualPronunciationList,
        alignedSyllabificationList,
        bestIndex,
    )


def _syllabifyPhones(phoneList: List[str], syllableList: List[List[str]]):
    """
    Given a phone list and a syllable list, syllabify the phones

    Typically used by findBestSyllabification which first aligns the phoneList
    with a dictionary phoneList and then uses the dictionary syllabification
    to syllabify the input phoneList.
    """

    numPhoneList = [len(syllable) for syllable in syllableList]

    start = 0
    syllabifiedList = []
    for end in numPhoneList:

        syllable = phoneList[start : start + end]
        syllabifiedList.append(syllable)

        start += end

    return syllabifiedList


def alignPronunciations(
    phoneListA: List[str], phoneListB: List[str]
) -> Tuple[List[str], List[str]]:
    """
    Align the phones in two pronunciations

    This will find the longest (non-continuous) common sequence and fill in the gaps
    before, between, and after the characters such that the common elements
    occur at the same points and the character strings are the same length

    In the following example, the phone lists share the sequence ['a', 'd']

    ```python
    phoneListA = ['a', 'b', 'c', 'd', 'e', 'f']
    phoneListB = ['l', 'a', 'z', 'd', 'u']
    a, b = alignPronunciations(phoneListA, phoneListB)
    print(a) > ["''", 'a', 'b', 'c', 'd', 'e', 'f']
    print(b) > ['l', 'a', 'z', "''", 'd', 'u', "''"]
    ```
    """

    # Remove any elements not in the other list (but maintain order)
    pronATmp = copy.deepcopy(phoneListA)
    pronBTmp = copy.deepcopy(phoneListB)

    # Find the longest sequence
    sequence = _lcs(pronBTmp, pronATmp)

    # Find the index of the sequence
    # TODO: investigate ambiguous cases
    startA = 0
    startB = 0
    sequenceIndexListA = []
    sequenceIndexListB = []
    for phone in sequence:
        startA = pronATmp.index(phone, startA)
        startB = pronBTmp.index(phone, startB)

        sequenceIndexListA.append(startA)
        sequenceIndexListB.append(startB)

    # An index on the tail of both will be used to create output strings
    # of the same length
    sequenceIndexListA.append(len(pronATmp))
    sequenceIndexListB.append(len(pronBTmp))

    # Fill in any blanks such that the sequential items have the same
    # index and the two strings are the same length
    for i, _ in enumerate(sequenceIndexListA):
        indexA = sequenceIndexListA[i]
        indexB = sequenceIndexListB[i]
        if indexA < indexB:
            for _ in range(indexB - indexA):
                pronATmp.insert(indexA, "''")
            sequenceIndexListA = [val + indexB - indexA for val in sequenceIndexListA]
        elif indexA > indexB:
            for _ in range(indexA - indexB):
                pronBTmp.insert(indexB, "''")
            sequenceIndexListB = [val + indexA - indexB for val in sequenceIndexListB]

    return pronATmp, pronBTmp


def findBestSyllabification(isleDict: isle.Isle, wordText: str, phoneList: List[str]):
    """
    Find the best syllabification for a word

    First find the closest pronunciation to a given pronunciation. Then take
    the syllabification for that pronunciation and map it onto the
    input pronunciation.
    """
    try:
        isleWordList = isleDict.lookup(wordText)[0]
    except errors.WordNotInISLE:
        # Many words are in the dictionary but not inflected forms
        # like the possesive (eg bob's)
        # If the word could not be found, try dropping the 's
        # and try searching again.
        if wordText[-2:] != "'s":
            raise

        isleWordList = isleDict.lookup(wordText[:-2])[0]

        for wordTuple in isleWordList:
            syllableList = wordTuple[0]  # syllableList, stressList
            finalSyllable = syllableList[-1]
            lastSound = finalSyllable[-1]

            if lastSound in phonetic_constants.alveolars:
                finalSyllable.append("ɪ")
            if lastSound in phonetic_constants.unvoiced:
                finalSyllable.append("s")
            else:
                finalSyllable.append("z")

    return _findBestSyllabification(isleWordList, phoneList)


def _findBestSyllabification(inputIsleWordList, actualPronunciationList):
    """
    Find the best syllabification for a word

    First find the closest pronunciation to a given pronunciation. Then take
    the syllabification for that pronunciation and map it onto the
    input pronunciation.
    """
    retList = _findBestPronunciation(inputIsleWordList, actualPronunciationList)
    isleWordList, alignedAPronList, alignedSyllableList, bestIndex = retList

    alignedPhoneList = alignedAPronList[bestIndex]
    alignedSyllables = alignedSyllableList[bestIndex]
    syllabification = isleWordList[bestIndex][0]
    stressedSyllableIndexList = isleWordList[bestIndex][1]
    stressedPhoneIndexList = isleWordList[bestIndex][2]

    syllableList = _syllabifyPhones(alignedPhoneList, alignedSyllables)

    # Get the location of stress in the generated file
    try:
        stressedSyllableI = stressedSyllableIndexList[0]
    except IndexError:
        stressedSyllableI = None
        stressedVowelI = None
    else:
        try:
            stressedVowelI = _getSyllableNucleus(syllableList[stressedSyllableI])
        except errors.TooManyVowelsInSyllable as err:
            raise errors.ImpossibleSyllabificationError(
                syllableList, alignedSyllables
            ) from err

    # Count the index of the stressed phones, if the stress list has
    # become flattened (no syllable information)
    flattenedStressIndexList = []
    for i, j in zip(stressedSyllableIndexList, stressedPhoneIndexList):
        k = j
        for m in range(i):
            k += len(syllableList[m])
        flattenedStressIndexList.append(k)

    return (
        stressedSyllableI,
        stressedVowelI,
        syllableList,
        syllabification,
        stressedSyllableIndexList,
        stressedPhoneIndexList,
        flattenedStressIndexList,
    )


def _getSyllableNucleus(phoneList: List[str]) -> Optional[int]:
    """
    Given the phones in a syllable, retrieves the vowel index
    """
    cvList = ["V" if isle.isVowel(phone) else "C" for phone in phoneList]

    vowelCount = cvList.count("V")
    if vowelCount > 1:
        raise errors.TooManyVowelsInSyllable(phoneList, cvList)

    stressI: Optional[int]
    if vowelCount == 1:
        stressI = cvList.index("V")
    else:
        stressI = None

    return stressI


def findClosestPronunciation(
    isleDict: isle.Isle, word: str, phoneList: List[str]
) -> constants.Syllabification:
    """
    Find the closest dictionary pronunciation to a provided pronunciation
    """
    isleWordList = isleDict.lookup(word)

    retList = _findBestPronunciation(isleWordList[0], phoneList)
    isleWordList = retList[0]
    bestIndex = retList[3]

    return isleWordList[bestIndex]
