# encoding: utf-8

import re
from typing import List, Optional, Tuple, Union, TypeVar
from abc import ABC

from pysle.utilities import errors
from pysle.utilities import phonetic_constants
from pysle.utilities import utils


def isVowel(char: str) -> bool:
    """Is this character a vowel?"""
    return any([vowel in char for vowel in phonetic_constants.vowelList])


T = TypeVar("T", bound="AbstractPhonemeList")


class AbstractPhonemeList(ABC):
    def __init__(self, phonemes: List[str]):
        self.phonemes = phonemes
        # self.__current = -1

    def __len__(self):
        return len(self.phonemes)

    def __eq__(self, other):
        return self.phonemes == other.phonemes

    # def __iter__(self):
    #     return self

    # def __next__(self):
    #     self.__current += 1
    #     if self.__current < len(self.phonemes):
    #         return self.phonemes[self.__current]
    #     else:
    #         raise StopIteration

    def stripDiacritics(self: T) -> T:
        # TODO: make more comprehensive
        newPhonemes = [re.sub("[˺ˌˈ]", "", phone) for phone in self.phonemes]
        return type(self)(newPhonemes)

    def simplify(self: T) -> T:
        """
        Simplifies pronunciation

        Removes diacritics and unifies vowels and rhotics
        """
        simplifiedPhones: List[str] = []
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


class PhonemeList(AbstractPhonemeList):
    def __add__(self, other: "PhonemeList"):
        return PhonemeList(self.phonemes + other.phonemes)

    def findBestSyllabification(self, entries: List["Entry"]) -> "Syllabification":
        return self._findClosestEntry(entries)[1].syllabificationList[0]

    def findClosestEntry(self, entries: List["Entry"]) -> "Entry":
        return self._findClosestEntry(entries)[0]

    def syllabify(self, syllabification: "Syllabification") -> "Syllabification":
        """
        Given a phone list and a syllable list, syllabify the phones

        Typically used by findBestSyllabification which first aligns the phoneList
        with a dictionary phoneList and then uses the dictionary syllabification
        to syllabify the input phoneList.
        """

        numPhoneList = [len(syllable) for syllable in syllabification.syllables]

        start = 0
        syllabifiedList = []
        for end in numPhoneList:

            syllable = self.phonemes[start : start + end]
            syllabifiedList.append(syllable)

            start += end

        # TODO: Resolve stress?
        return Syllabification(syllabifiedList, [], [])

    def align(
        self, targetPhoneList: "PhonemeList", simplifiedMatching: bool
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

        def _undoSimplification(
            rawPhones: List[str], phonemeList: "PhonemeList"
        ) -> "PhonemeList":
            rawPhones = rawPhones[:]
            return PhonemeList(
                [
                    rawPhones.pop(0)
                    if phon != phonetic_constants.FILLER
                    else phonetic_constants.FILLER
                    for phon in phonemeList.phonemes
                ]
            )

        if simplifiedMatching:
            alignedSelf, alignedTarget = self.simplify()._align(
                targetPhoneList.simplify()
            )
            alignedSelf = _undoSimplification(self.phonemes, alignedSelf)
            alignedTarget = _undoSimplification(targetPhoneList.phonemes, alignedTarget)
        else:
            alignedSelf, alignedTarget = self._align(targetPhoneList)

        return alignedSelf, alignedTarget

    def _findClosestEntry(self, entries: List["Entry"]) -> Tuple["Entry", "Entry"]:
        numDiffList: List[int] = []
        withStress: List[bool] = []

        modifiedSyllabificationLists: List[Syllabification] = []
        for entry in entries:
            # TODO: Add support for multi-word entries
            if len(entry.syllabificationList) > 1:
                raise errors.PysleException(
                    "findClosestEntry does not support multi-word lookup (yet).  Please file an issue to bump priority."
                )

            targetSyllabification = entry.syllabificationList[0]
            adjustedPhoneList, adjustedTargetPhoneList = self.align(
                targetSyllabification.desyllabify(), simplifiedMatching=True
            )

            numDiff = adjustedPhoneList.phonemes.count(phonetic_constants.FILLER)
            numDiff += adjustedTargetPhoneList.phonemes.count(phonetic_constants.FILLER)
            numDiffList.append(numDiff)

            withStress.append(entry.hasStress)

            modifiedSyllabificationLists.append(
                targetSyllabification._adjustSyllabification(adjustedTargetPhoneList)
            )

        bestIndex = _chooseMostSimilarWithStress(numDiffList, withStress)

        if bestIndex is None:
            raise errors.PysleException(
                "Unexpected error: Could not choose a closest pronunciation."
            )
        closestEntry = entries[bestIndex]

        modifiedTargetSyllabification = modifiedSyllabificationLists[bestIndex]
        constructedEntry = Entry(
            closestEntry.word, [modifiedTargetSyllabification], closestEntry.posList
        )

        return (closestEntry, constructedEntry)

    def _align(
        self, targetPhoneList: "PhonemeList"
    ) -> Tuple["PhonemeList", "PhonemeList"]:
        """See align()"""

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
                    pronATmp.insert(indexA, phonetic_constants.FILLER)
                sequenceIndexListA = [
                    val + indexB - indexA for val in sequenceIndexListA
                ]
            elif indexA > indexB:
                for _ in range(indexA - indexB):
                    pronBTmp.insert(indexB, phonetic_constants.FILLER)
                sequenceIndexListB = [
                    val + indexA - indexB for val in sequenceIndexListB
                ]

        return type(self)(pronATmp), type(self)(pronBTmp)


class Syllable(AbstractPhonemeList):
    def __init__(self, phonemes: List[str]):
        self.cvList = ["V" if isVowel(phone) else "C" for phone in phonemes]

        vowelCount = self.cvList.count("V")
        if vowelCount > 1:
            raise errors.TooManyVowelsInSyllable(phonemes, self.cvList)

        super(Syllable, self).__init__(phonemes)

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
    def nucleus(self) -> Optional[str]:
        """
        Given the phones in a syllable, retrieves the vowel index
        """
        vowelCount = self.cvList.count("V")

        stressI: Optional[int]
        if vowelCount == 1:
            stressI = self.cvList.index("V")
            return self.phonemes[stressI]
        else:
            return None


class Syllabification(object):
    def __init__(
        self,
        syllables: Union[List[Syllable], List[List[str]]],
        stressedSyllableIndicies: List[int] = None,
        stressedVowelIndicies: List[int] = None,
    ):
        self.syllables = [_toSyllables(syllable) for syllable in syllables]
        self.stressedSyllableIndicies = stressedSyllableIndicies
        self.stressedVowelIndicies = stressedVowelIndicies

    @classmethod
    def new(cls, syllables: Union[List[Syllable], List[List[str]]]):
        stressedSyllableIndicies, stressedVowelIndicies = _findStress(syllables)
        return Syllabification(
            syllables, stressedSyllableIndicies, stressedVowelIndicies
        )

    def __len__(self):
        return len(self.syllables)

    def __eq__(self, other):
        isEqual = True
        isEqual &= self.syllables == other.syllables
        isEqual &= self.stressedSyllableIndicies == other.stressedSyllableIndicies
        isEqual &= self.stressedVowelIndicies == other.stressedVowelIndicies

        return isEqual

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

    def toList(self) -> List[List[str]]:
        return [syllable.phonemes for syllable in self.syllables]

    def desyllabify(self) -> PhonemeList:
        return PhonemeList(
            [phone for syllable in self.syllables for phone in syllable.phonemes]
        )

    def morph(self, targetSyllabification: "Syllabification") -> "Syllabification":
        """
        Morph this syllabification to be like the target (in what way?)
        """
        currentPhoneList = self.desyllabify()
        targetPhoneList = targetSyllabification.desyllabify()

        # Make the two pronunciations the same length (using a simplified version of each)
        alignedP, _ = currentPhoneList.align(targetPhoneList, simplifiedMatching=True)

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

                numBlanks = tmpPhoneList.count(phonetic_constants.FILLER)
                if numBlanks > 0:
                    tmpPhoneList = adjustedPhoneList.phonemes[i + j : i + j + numBlanks]
                    phoneList.extend(tmpPhoneList)
                    j += numBlanks

            for k, phone in enumerate(phones):
                if phone == phonetic_constants.FILLER:
                    phones.insert(k, phonetic_constants.FILLER)

            i += j

            retSyllableList.append(phones)

        # TODO: What to do about stress?
        return Syllabification(retSyllableList, [], [])


class Entry(object):
    def __init__(
        self,
        word: str,
        syllabificationList: Union[List[Syllabification], List[List[List[str]]]],
        posList: List[str],
    ):
        self.word = word
        self.syllabificationList = [
            _toSyllabification(syllabification)
            for syllabification in syllabificationList
        ]
        self.posList = posList

    def __eq__(self, other):
        isEqual = True
        isEqual &= self.word == other.word
        isEqual &= self.syllabificationList == other.syllabificationList
        isEqual &= self.posList == other.posList

        return isEqual

    @property
    def hasStress(self) -> bool:
        for syllabification in self.syllabificationList:
            if syllabification.hasStress:
                return True

        return False

    @property
    def phonemeList(self) -> PhonemeList:
        phoneList = PhonemeList([])
        for syllabification in self.syllabificationList:
            phoneList = phoneList + syllabification.desyllabify()

        return phoneList

    def toList(self) -> List[List[List[str]]]:
        return [
            syllabification.toList() for syllabification in self.syllabificationList
        ]

    def findClosestPronunciation(
        self, entries: List["Entry"]
    ) -> Tuple["Entry", "Entry"]:
        """
        Returns the entry from the given list that is most like this entry
        """

        def diffCount(
            currentSyllabification, targetSyllabification: "Syllabification"
        ) -> int:
            currentPhoneList = currentSyllabification.desyllabify()
            targetPhoneList = targetSyllabification.desyllabify()

            # Make the two pronunciations the same length (using a simplified version of each)
            alignedP, alignedTargetP = currentPhoneList.align(
                targetPhoneList, simplifiedMatching=True
            )

            return alignedP.phonemes.count(
                phonetic_constants.FILLER
            ) + alignedTargetP.phonemes.count(phonetic_constants.FILLER)

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
                numDiff += diffCount(syllabification, targetSyllabification)

                if entry.hasStress:
                    hasStress = True

            numDiffList.append(numDiff)
            withStress.append(hasStress)
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


def _toPhonemeList(phoneList: Union[PhonemeList, List[str]]) -> PhonemeList:
    if isinstance(phoneList, list):
        return PhonemeList(phoneList)
    elif isinstance(phoneList, PhonemeList):
        return phoneList

    raise AttributeError


def _toSyllabification(
    syllabification: Union[Syllabification, List[List[str]]]
) -> Syllabification:
    if isinstance(syllabification, list):
        return Syllabification.new(syllabification)
    elif isinstance(syllabification, Syllabification):
        return syllabification

    raise AttributeError


def _toSyllables(syllable: Union[Syllable, List[str]]) -> Syllable:
    if isinstance(syllable, list):
        return Syllable(syllable)
    elif isinstance(syllable, Syllable):
        return syllable

    raise AttributeError


def _chooseMostSimilarWithStress(
    numDiffList: List[int], withStress: List[bool]
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
            bestIsStressed = withStress[i]
        else:
            if not bestIsStressed and withStress[i]:
                bestIndex = i
                bestIsStressed = True

    return bestIndex


def _findStress(
    syllables: Union[List[Syllable], List[List[str]]]
) -> Tuple[List[int], List[int]]:

    stressedSyllables: List[int] = []
    stressedPhones: List[int] = []
    for syllableI, syllable in enumerate(syllables):

        if isinstance(syllable, Syllable):
            phonemes = syllable.phonemes
        elif isinstance(syllable, List):
            phonemes = syllable
        else:
            raise AttributeError

        for phoneI, phone in enumerate(phonemes):
            if u"ˈ" in phone:
                stressedSyllables.insert(0, syllableI)
                stressedPhones.insert(0, phoneI)
                break

            if u"ˌ" in phone:
                stressedSyllables.append(syllableI)
                stressedPhones.append(phoneI)

    return stressedSyllables, stressedPhones
