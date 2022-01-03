# encoding: utf-8
"""Data types for representing Isle dictionaries entries and pronunciations
"""

import re
from typing import List, Optional, Tuple, Union, TypeVar
from abc import ABC

from typing_extensions import Literal

from pysle.utilities import errors
from pysle.utilities import constants
from pysle.utilities import phonetic_constants
from pysle.utilities import utils


def isVowel(char: str) -> bool:
    return any([vowel in char for vowel in phonetic_constants.vowelList])


def isRhotic(char: str) -> bool:
    return any([rhotic in char for rhotic in phonetic_constants.rhotics])


T = TypeVar("T", bound="AbstractPhonemeList")


class AbstractPhonemeList(ABC):
    """Base class for a list of phonemes"""

    def __init__(self, phonemes: List[str]):
        if any([len(phone) == 0 for phone in phonemes]):
            raise errors.NullPhoneError()

        self.phonemes = phonemes

    def __len__(self):
        return len(self.phonemes)

    def __eq__(self, other):
        if type(self) != type(other):
            return False

        return self.phonemes == other.phonemes

    def stripDiacritics(self: T) -> T:
        """Removes diacritics from phones"""
        # TODO: make more comprehensive
        newPhonemes = [re.sub("[˺ˌˈ]", "", phone) for phone in self.phonemes]
        return type(self)(newPhonemes)

    def simplify(self: T) -> T:
        """Simplifies pronunciation

        - Removes diacritics
        - Unifies vowels and rhotics
        - Reduces all phonemes to one character
        """
        simplifiedPhones: List[str] = []
        for phone in self.phonemes:
            for diacritic in phonetic_constants.diacriticList:
                phone = phone.replace(diacritic, "")

            phone = phone.lower()
            if isRhotic(phone):  # Unify rhotics
                phone = "r"
            elif isVowel(phone):
                phone = "V"
            else:
                phone = phone[0]

            simplifiedPhones.append(phone)

        return type(self)(simplifiedPhones)


class PhonemeList(AbstractPhonemeList):
    """A list of phonemes

    Attributes:
        phonemes: The list of phonemes
    """

    def __add__(self, other: "PhonemeList"):
        return PhonemeList(self.phonemes + other.phonemes)

    def findBestSyllabification(
        self,
        entries: List["Entry"],
    ) -> "Syllabification":
        """Finds the closest entry to the PhonemeList and uses it as the model Syllabification

        'Closeness' is determined by similarity in PhoneLists.  See
        PhoneList._findClosestEntry() for details.
        """
        syllabification = self._findClosestEntry(entries)[1].syllabificationList[0]
        return self.syllabify(
            syllabification, onSizeError=constants.ErrorReportingMode.SILENCE
        )

    def findClosestEntry(self, entries: List["Entry"]) -> "Entry":
        """
        Finds the closest Entry to this PhonemeList

        'Closeness' is determined by similarity in PhoneLists.  See
        PhoneList._findClosestEntry() for details.
        """
        return self._findClosestEntry(entries)[0]

    def syllabify(
        self,
        syllabification: "Syllabification",
        onSizeError: Literal["silence", "warning", "error"] = "warning",
    ) -> "Syllabification":
        """Up convert a PhonemeList to a Syllabification

        This requires a syllabification to model after. This is a best-effort
        conversion. For best results, the syllabification should be as close
        to this phone list, in terms of phones.

        Args:
            syllabification: the model syllabification to map onto this PhonemeList
            onSizeError: determines the behavior when the syllabification has a
                different number of phonemes from this PhonemeList

        Returns:
            a Syllabification of this PhonemeList

        Raises:
            SyllabificationError: when the length of the PhonemeList does not match the
                model Syllabification
        """
        utils.validateOption("onSizeError", onSizeError, constants.ErrorReportingMode)
        errorReporter = utils.getErrorReporter(onSizeError)

        numPhoneList = [len(syllable) for syllable in syllabification.syllables]

        start = 0
        syllabifiedList = []
        for end in numPhoneList:

            syllable = self.phonemes[start : start + end]
            if len(syllable) > 0:
                syllabifiedList.append(syllable)

            start += end

        targetLen = len(syllabification)
        actualLen = len(syllabifiedList)
        targetNumPhones = len(syllabification.desyllabify())

        if targetLen > actualLen:
            errorReporter(
                errors.SyllabificationError,
                f"The target syllabification ({syllabification.toList()}) is too long for the input "
                f"({self.phonemes}); the output has been truncated ({syllabifiedList})",
            )
        elif targetNumPhones != len(self.phonemes):
            errorReporter(
                errors.SyllabificationError,
                f"The target syllabification ({syllabification.toList()}) is too short for the input "
                f"({self.phonemes}); the best fit syllabification output is ({syllabifiedList})",
            )

        # TODO: Resolve stress properly?
        return Syllabification(syllabifiedList, [], [])

    def align(
        self, targetPhoneList: "PhonemeList", simplifiedMatching: bool
    ) -> Tuple["PhonemeList", "PhonemeList"]:
        """Align the phones in two pronunciations

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

        Args:
            targetPhoneList: the PhoneList to align with the current PhoneList
            simplifiedMatching: if True, use a simplified version of phones, which
                allows for looser matching; if False, characters must match exactly
                as is

        Returns:
            this PhoneList and the targetPhoneList, aligned in length

        Raises:
            UnexpectedError: hopefully you should never see this
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

        if len(alignedSelf) != len(alignedTarget):
            raise errors.UnexpectedError(
                "Source and target phone lengths are different but should be the same. "
                f"({alignedSelf.phonemes}), ({alignedTarget.phonemes}).  Please report to the developers."
            )

        return alignedSelf, alignedTarget

    def _findClosestEntry(self, entries: List["Entry"]) -> Tuple["Entry", "Entry"]:
        """Finds the closest Entry out of those in a list to the current PhonemeList

        Entries are first aligned with this PhonemeList. The entry with the fewest
        number of changes needed in alignment is considered to be the closest entry.

        Args:
            entries: the entries to search through

        Returns:
            both the closest entry and a modified version of the closest entry,
            morphed to be similar to the source PhonemeList

        Raises:
            FeatureNotYetAvailableError: For multi-word entries
        """
        numDiffList: List[int] = []
        withStress: List[bool] = []

        modifiedSyllabificationLists: List[Syllabification] = []
        targetPhoneListCandidates: List[PhonemeList] = []
        for entry in entries:
            # TODO: Add support for multi-word entries (seems tedious for little benefit?)
            if len(entry.syllabificationList) > 1:
                raise errors.FeatureNotYetAvailableError(
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
                targetSyllabification._postAlignAdjustment(adjustedTargetPhoneList)
            )

        bestIndex = _chooseMostSimilarWithStress(numDiffList, withStress)

        if bestIndex is None:
            raise errors.ClosestEntryError(
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
        """See PhonemeList.align()"""

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

            startA += 1
            startB += 1

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
    """A list of phonemes that compose a single Syllable

    Attributes:
        phonemes (List[str]): the list of phonemes in this syllable
        cvList (List[str]): the consonant/vowel structure of the syllable
        hasStress (bool): True if the syllable carries stress; False if not
        hasSecondaryStress (bool): True if the syllable carries secondary
            stress; False if not
        nucleus (str): most typically the vowel of the syllable; None if the
            vowel can't be detected
    """

    def __init__(self, phonemes: List[str]):
        self.cvList = ["V" if isVowel(phone) else "C" for phone in phonemes]

        vowelCount = self.cvList.count("V")
        if vowelCount > 1:
            raise errors.TooManyVowelsInSyllableError(phonemes, self.cvList)

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
        """Typically the vowel in a syllable"""
        vowelCount = self.cvList.count("V")

        stressI: Optional[int]
        if vowelCount == 1:
            stressI = self.cvList.index("V")
            return self.phonemes[stressI]
        else:
            return None


class Syllabification:
    """Representation of athe phones in an utterance, divided into syllables

    Attributes:
        hasStress (bool): True if there is stress in this syllable; False if not
        stress (List[int]): a list containing first the index of the stressed
            syllable, followed by the indicies of syllables containing secondary
            stress
    """

    def __init__(
        self,
        syllables: Union[List[Syllable], List[List[str]]],
        stressedSyllableIndicies: List[int] = None,
        stressedVowelIndicies: List[int] = None,
    ):
        """Constructor for a Syllabification

        Args:
            syllables: a list of syllables representing a word
            stressedSyllableIndicies: the location of stressed syllables;
                primary stress should appear in the first position, followed
                by secondary stress
            stressedVowelIndicies: the location of stressed vowels, with
                respect to the syllables that they occur in
        """
        self.syllables = [
            _toSyllable(syllable) for syllable in syllables if len(syllable) > 0
        ]
        self.stressedSyllableIndicies: List[int] = (
            stressedSyllableIndicies if stressedSyllableIndicies is not None else []
        )
        self.stressedVowelIndicies: List[int] = (
            stressedVowelIndicies if stressedVowelIndicies is not None else []
        )

    @classmethod
    def new(_cls, syllables: Union[List[Syllable], List[List[str]]]):
        """Overloaded constructor for Syllabification

        Stress information is be inferred from annotations on the syllables

        Args:
            syllables: a list of syllables representing a word
        """
        stressedSyllableIndicies, stressedVowelIndicies = _findStress(syllables)
        return Syllabification(
            syllables, stressedSyllableIndicies, stressedVowelIndicies
        )

    def __len__(self):
        return len(self.syllables)

    def __eq__(self, other):
        if not isinstance(other, Syllabification):
            return False

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
        # TODO: Why do we have this property and stressedSyllableIndicies?
        stressList = []
        for i, syllable in enumerate(self.syllables):
            if syllable.hasStress:
                stressList.append(i)

        for j, syllable in enumerate(self.syllables):
            if syllable.hasSecondaryStress:
                stressList.append(j)

        return stressList

    def toList(self) -> List[List[str]]:
        """Syllabification in plain list representation"""
        return [syllable.phonemes for syllable in self.syllables]

    def desyllabify(self) -> PhonemeList:
        """Down convert this Syllabification to a PhonemeList"""
        return PhonemeList(
            [phone for syllable in self.syllables for phone in syllable.phonemes]
        )

    def stretch(self, targetSyllabification: "Syllabification") -> "Syllabification":
        """Lengthen the source syllabification based on a target syllabification

        This works by first desllabifying the two syllabifications, adjusting the
        length by inserting spaces, and then resyllabifying.  The target's syllable
        structure has no influence on the output.

        ```python
        a = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        b = phonetics.Syllabification([["p", "m"], ["k", "ɪ", "n"]])
        print(a.stretch(b).toList())
        >> [["p", "m"], ["k", "''", "n"]]
        ```

        TODO: The more different the source and target are, the more meaningless
              the results become.
        """
        # Make the two pronunciations the same length
        alignedP, _ = self.desyllabify().align(
            targetSyllabification.desyllabify(), simplifiedMatching=True
        )

        return self._postAlignAdjustment(alignedP)

    def _postAlignAdjustment(self, adjustedPhoneList: PhonemeList) -> "Syllabification":
        """Inserts spaces into a syllable if needed

        Originally this Syllabification and the adjustedPhoneList
        contained the same number of phones.  But the adjustedPhoneList
        may have some insertions which are not accounted for in the
        syllableList.
        """
        # TODO: This method is spagetti code
        i = 0
        retSyllableList = []
        for syllableNum, syllable in enumerate(self.syllables):
            phones = syllable.phonemes[:]
            j = len(phones)
            if syllableNum == len(self) - 1:
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

            for k, phone in enumerate(phoneList):
                if phone == phonetic_constants.FILLER:
                    phones.insert(k, phonetic_constants.FILLER)

            i += j

            retSyllableList.append(phones)

        # TODO: What to do about stress?
        return Syllabification(retSyllableList, [], [])


class Entry:
    """Representation for a single line in the Isle dictionary

    Attributes:
        word: the word for this Entry (eg 'cat')
        syllabificationList: the syllabification for this Entry
            (eg [[['k', 'a', 't']]]); it's represented by a List of Lists
            of Lists of strings because:
            - multiple words can be part of the same entry
            - each word can have multiple syllables
            - each syllable can have multiple phones
        phonemeList: the syllabification in this entry, with syllable
            information removed
        posList: the part of speech associated with this word
        hasStress: True if the syllabification in this entry contains stress
    """

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
        if not isinstance(other, Entry):
            return False

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

    def toDict(self):
        return {
            "word": self.word,
            "syllabificationList": self.toList(),
            "posList": self.posList,
        }

    def findClosestPronunciation(
        self, entries: List["Entry"]
    ) -> Tuple["Entry", "Entry"]:
        """Returns the entry from the given list that is most like this entry

        Similarity between entries is done by comparing desyllabified forms
        """

        def diffCount(
            currentSyllabification, targetSyllabification: "Syllabification"
        ) -> int:
            currentPhoneList = currentSyllabification.desyllabify()
            targetPhoneList = targetSyllabification.desyllabify()

            # Make the two pronunciations the same length (using a simplified
            # version of each)
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
                    targetSyllabification.stretch(syllabification)
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
            raise errors.FindClosestError(
                "Unexpected error: Could not choose a closest pronunciation."
            )
        closestEntry = entries[bestIndex]

        modifiedTargetSyllabification = modifiedSyllabificationListsOrderedByEntry[
            bestIndex
        ]
        constructedEntry = Entry(self.word, modifiedTargetSyllabification, self.posList)

        return (closestEntry, constructedEntry)


def _toPhonemeList(phoneList: Union[PhonemeList, List[str]]) -> PhonemeList:
    """Utility function to unify the input to be PhonemeList"""
    if isinstance(phoneList, list):
        return PhonemeList(phoneList)
    elif isinstance(phoneList, PhonemeList):
        return phoneList

    raise AttributeError


def _toSyllabification(
    syllabification: Union[Syllabification, List[List[str]]]
) -> Syllabification:
    """Utility function to unify the input to be a Syllabification"""
    if isinstance(syllabification, list):
        return Syllabification.new(syllabification)
    elif isinstance(syllabification, Syllabification):
        return syllabification

    raise AttributeError


def _toSyllable(syllable: Union[Syllable, List[str]]) -> Syllable:
    """Utility function to unify the input to be a Syllable"""
    if isinstance(syllable, list):
        return Syllable(syllable)
    elif isinstance(syllable, Syllable):
        return syllable

    raise AttributeError


def _chooseMostSimilarWithStress(
    numDiffList: List[int], withStress: List[bool]
) -> Optional[int]:
    """Choose the index with the smallest number of differences; prefer stressed options

    If two indicies are tied for the smallest number of differences, choose a stressed
    one over an unstressed.

    If two indicies are tied for the smallest number of differences and are equal in
    stress status, choose the first option.

    numDiffList and withStress should be the same length
    """
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
    """Find the syllable and phone indicies for stress annotations"""
    tmpSyllables = [_toSyllable(syllable) for syllable in syllables]

    stressedSyllables: List[int] = []
    stressedPhones: List[int] = []
    for syllableI, syllable in enumerate(tmpSyllables):
        for phoneI, phone in enumerate(syllable.phonemes):
            if "ˈ" in phone:
                stressedSyllables.insert(0, syllableI)
                stressedPhones.insert(0, phoneI)
                break

            if "ˌ" in phone:
                stressedSyllables.append(syllableI)
                stressedPhones.append(phoneI)

    return stressedSyllables, stressedPhones
