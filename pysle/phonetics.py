# encoding: utf-8

import io
import re
import os
from pkg_resources import resource_filename
from typing import List, Optional, Dict, Tuple, Union
from typing_extensions import Literal

from pysle.utilities import errors
from pysle.utilities import phonetic_constants
from pysle.utilities import isle_io
from pysle.utilities import utils


def isVowel(char: str) -> bool:
    """Is this character a vowel?"""
    return any([vowel in char for vowel in phonetic_constants.vowelList])


class PhonemeList(object):
    def __init__(self, phonemes: List[str]):
        self.phonemes = phonemes

    def __len__(self):
        return len(self.phonemes)

    def syllabify(self, syllabification: "Syllabification") -> "Syllabification":
        """
        Given a phone list and a syllable list, syllabify the phones

        Typically used by findBestSyllabification which first aligns the phoneList
        with a dictionary phoneList and then uses the dictionary syllabification
        to syllabify the input phoneList.

        This only makes sense for a PhonemeList that is not a syllible.
        TODO: Consider splitting PhonemeList into Syllable and PhonemeListing
        """

        numPhoneList = [len(syllable) for syllable in syllabification.syllables]

        start = 0
        syllabifiedList = []
        for end in numPhoneList:

            syllable = self.phonemes[start : start + end]
            syllabifiedList.append(syllable)

            start += end

        return Syllabification(syllabifiedList, [], [])

    def simplify(self) -> "PhonemeList":
        """
        Simplifies pronunciation

        Removes diacritics and unifies vowels and rhotics
        """
        simplifiedPhones = []
        for phone in self.phonemes:
            for diacritic in phonetic_constants.diacriticList:
                phone = phone.replace(diacritic, "")

            phone = phone.lower()
            if "r" in phone:  # Unify rhotics
                phone = "r"
            elif isVowel(phone):
                phone = "V"
            else:
                try:
                    phone = phone[0]
                except IndexError:
                    raise errors.NullPhoneError()

            simplifiedPhones.append(phone)

        return type(self)(simplifiedPhones)

    def align(
        self, targetPhoneList: "PhonemeList"
    ) -> Tuple["PhonemeList", "PhonemeList"]:
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
        pronATmp = self.phonemes[:]
        pronBTmp = targetPhoneList.phonemes[:]

        # Find the longest sequence
        sequence = utils._lcs(pronBTmp, pronATmp)

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
                sequenceIndexListA = [
                    val + indexB - indexA for val in sequenceIndexListA
                ]
            elif indexA > indexB:
                for _ in range(indexA - indexB):
                    pronBTmp.insert(indexB, "''")
                sequenceIndexListB = [
                    val + indexA - indexB for val in sequenceIndexListB
                ]

        return type(self)(pronATmp), type(self)(pronBTmp)


class Syllable(PhonemeList):
    @property
    def hasStress(self) -> bool:
        for phone in self.phonemes:
            if "ˈ" in phone:
                return True

        return False

    @property
    def hasSecondaryStress(self) -> bool:
        for phone in self.phonemes:
            if "ˌ" in phone:
                return True

        return False

    @property
    def nucleus(self) -> Optional[int]:
        """
        Given the phones in a syllable, retrieves the vowel index
        """
        cvList = ["V" if isVowel(phone) else "C" for phone in self.phonemes]

        vowelCount = cvList.count("V")
        if vowelCount > 1:
            raise errors.TooManyVowelsInSyllable(self.phonemes, cvList)

        stressI: Optional[int]
        if vowelCount == 1:
            stressI = cvList.index("V")
        else:
            stressI = None

        return stressI


class Pronunciation(object):
    def __init__(self, pronunciation, posList: List[str]):
        self.pronunciation = pronunciation
        self.posList = posList


class Syllabification(object):
    def __init__(
        self,
        syllables: Union[List[Syllable], List[List[str]]],
        stressedSyllableIndicies: List[int],
        stressedVowelIndicies: List[int],
    ):
        self.syllables = [_toSyllableList(syllable) for syllable in syllables]
        self.stressedSyllableIndicies = stressedSyllableIndicies
        self.stressedVowelIndicies = stressedVowelIndicies

    def __len__(self):
        return len(self.syllables)

    @property
    def hasStress(self) -> bool:
        for syllable in self.syllables:
            if syllable.hasStress:
                return True

        return False

    @property
    def stress(self) -> List[int]:
        stressList = []
        for i, syllable in enumerate(self.syllables):
            if syllable.hasStress:
                stressList.append(i)

        for j, syllable in enumerate(self.syllables):
            if syllable.hasSecondaryStress:
                stressList.append(j)

        return stressList

    def desyllabify(self) -> PhonemeList:
        return PhonemeList(
            [phone for syllable in self.syllables for phone in syllable.phonemes]
        )

    def diffCount(self, targetSyllabification: "Syllabification") -> int:
        dictionaryPronunciation = self.desyllabify()
        targetDictionaryPronunciation = targetSyllabification.desyllabify()

        # Make the two pronunciations the same length (using a simplified version of each)
        alignedP, alignedTargetP = dictionaryPronunciation.simplify().align(
            targetDictionaryPronunciation.simplify()
        )

        return alignedP.phonemes.count("''") + alignedTargetP.phonemes.count("''")

    def morph(self, targetSyllabification: "Syllabification") -> "Syllabification":
        """
        Morph this syllabification to be like the target
        """
        dictionaryPronunciation = self.desyllabify()
        targetDictionaryPronunciation = targetSyllabification.desyllabify()

        # Make the two pronunciations the same length (using a simplified version of each)
        alignedP, _ = dictionaryPronunciation.simplify().align(
            targetDictionaryPronunciation.simplify()
        )

        # Undo the phonetic simplification
        alignedP = PhonemeList(
            [
                dictionaryPronunciation.phonemes.pop(0) if phon != "''" else "''"
                for phon in alignedP.phonemes
            ]
        )

        return self._adjustSyllabification(alignedP)

    def _adjustSyllabification(
        self, adjustedPhoneList: PhonemeList
    ) -> "Syllabification":
        """
        Inserts spaces into a syllable if needed

        Originally the phone list and syllable list contained the same number
        of phones.  But the adjustedPhoneList may have some insertions which are
        not accounted for in the syllableList.

        Adjusting the syllabification for differences between the dictionary
        pronunciation and the actual pronunciation
        """
        i = 0
        retSyllableList = []
        for syllableNum, syllable in enumerate(self.syllables):
            phones = syllable.phonemes[:]
            j = len(phones)
            if syllableNum == len(self.syllables) - 1:
                j = len(adjustedPhoneList.phonemes) - i
            tmpPhoneList = adjustedPhoneList.phonemes[i : i + j]
            numBlanks = -1
            phoneList = tmpPhoneList[:]
            while numBlanks != 0:

                numBlanks = tmpPhoneList.count("''")
                if numBlanks > 0:
                    tmpPhoneList = adjustedPhoneList.phonemes[i + j : i + j + numBlanks]
                    phoneList.extend(tmpPhoneList)
                    j += numBlanks

            for k, phone in enumerate(phones):
                if phone == "''":
                    phones.insert(k, "''")

            i += j

            retSyllableList.append(phones)

        # TODO: What to do about stress?
        return Syllabification(retSyllableList, [], [])


class Entry(object):
    def __init__(
        self, word: str, syllabificationList: List[Syllabification], posList: List[str]
    ):
        self.word = word
        self.syllabificationList = syllabificationList
        self.posList = posList

    @property
    def hasStress(self) -> bool:
        for syllabification in self.syllabificationList:
            if syllabification.hasStress:
                return True

        return False

    def findClosestPronunciation(
        self, entries: List["Entry"]
    ) -> Tuple["Entry", "Entry"]:
        """
        Returns the entry from the given list that is most like this entry
        """
        numDiffList = []
        withStress = []
        i = 0
        modifiedSyllabificationListsOrderedByEntry: List[List[Syllabification]] = []
        for entry in entries:
            assert len(entry.syllabificationList) == len(self.syllabificationList)

            numDiff = 0
            hasStress = False
            modifiedSyllabificationList: List[Syllabification] = []
            for syllabification, targetSyllabification in zip(
                entry.syllabificationList, self.syllabificationList
            ):
                modifiedSyllabificationList.append(
                    targetSyllabification.morph(syllabification)
                )
                numDiff += targetSyllabification.diffCount(syllabification)

                if entry.hasStress:
                    hasStress = True

            numDiffList.append(numDiff)
            if hasStress:
                withStress.append(i)
            modifiedSyllabificationListsOrderedByEntry.append(
                modifiedSyllabificationList
            )

            i += 1

        bestIndex = _chooseMostSimilarWithStress(numDiffList, withStress)

        if bestIndex is None:
            raise errors.PysleException(
                "Unexpected error: Could not choose a closest pronunciation."
            )
        closestEntry = entries[bestIndex]

        modifiedTargetSyllabification = modifiedSyllabificationListsOrderedByEntry[
            bestIndex
        ]
        constructedEntry = Entry(self.word, modifiedTargetSyllabification, self.posList)

        return (closestEntry, constructedEntry)


def _toSyllableList(syllable: Union[Syllable, List[str]]) -> Syllable:
    if type(syllable) == list:
        return Syllable(syllable)
    elif type(syllable) == Syllable:
        return syllable

    raise AttributeError


def _chooseMostSimilarWithStress(
    numDiffList: List[int], withStress: List[int]
) -> Optional[int]:
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

    return bestIndex
