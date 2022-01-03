# encoding: utf-8

from typing import List


class PysleException(Exception):
    pass


class ClosestEntryError(PysleException):
    pass


class UnexpectedError(PysleException):
    pass


class SyllabificationError(PysleException):
    pass


class FeatureNotYetAvailableError(PysleException):
    pass


class FindClosestError(PysleException):
    pass


class WordNotInIsleError(PysleException):
    def __init__(self, word: str):
        super(WordNotInIsleError, self).__init__()
        self.word = word

    def __str__(self):
        return (
            "Word '%s' not in ISLE dictionary.  "
            "Please add it to continue." % self.word
        )


class IsleDictDoesNotExistError(PysleException):
    def __str__(self):
        return (
            "You are trying to load a custom ISLE dictionary file that does not exist.\n"
            "By default, the original ISLE dictionary file will be loaded.\n"
            "If you want to use a custom ISLE dictionary, make sure the file exists "
            "and try again with the full path."
        )


class WrongOptionError(PysleException):
    def __init__(self, argumentName: str, givenValue: str, availableOptions: List[str]):
        self.argumentName = argumentName
        self.givenValue = givenValue
        self.availableOptions = availableOptions

    def __str__(self):
        return (
            f"For argument '{self.argumentName}' was given the value '{self.givenValue}'. "
            f"However, expected one of [{', '.join(self.availableOptions)}]"
        )


class OptionalFeatureError(ImportError):
    def __str__(self):
        return "ERROR: You must have praatio installed to use pysle.praatTools"


class TooManyVowelsInSyllableError(PysleException):
    def __init__(self, syllable: List[str], syllableCVMapped: List[str]):
        super(TooManyVowelsInSyllableError, self).__init__()
        self.syllable = syllable
        self.syllableCVMapped = syllableCVMapped

    def __str__(self):
        syllableStr = ",".join(self.syllable)
        syllableCVStr = "".join(self.syllableCVMapped)
        return (
            f"Error: syllable '{syllableStr}' found to have more than "
            f"one vowel.\n This was the CV mapping: '{syllableCVStr}'"
        )


class ImpossibleSyllabificationError(PysleException):
    def __init__(
        self,
        estimatedActualSyllabificationList: List[str],
        isleSyllabificationList: List[str],
    ):
        self.estimatedList = estimatedActualSyllabificationList
        self.isleSyllabificationList = isleSyllabificationList

    def __str__(self):
        return (
            f"Impossible syllabification; "
            f"Estimated: {self.estimatedList}; "
            f"ISLE's: {self.isleSyllabificationList}"
        )


class NumWordsMismatchError(PysleException):
    def __init__(self, word: str, numMatches: int):
        super(NumWordsMismatchError, self).__init__()
        self.word = word
        self.numMatches = numMatches

    def __str__(self):
        errStr = (
            "Error: %d matches found in isleDict for '%s'.\n"
            "Only 1 match allowed--likely you need to break"
            "up your query text into separate words."
        )
        return errStr % (self.numMatches, self.word)


class WrongTypeError(PysleException):
    def __init__(self, errMsg: str):
        super(WrongTypeError, self).__init__()
        self.str = errMsg

    def __str__(self):
        return self.str


class NullPronunciationError(PysleException):
    def __init__(self, word: str):
        super(NullPronunciationError, self).__init__()
        self.word = word

    def __str__(self):
        return "No pronunciation given for word '%s'" % self.word


class NullPhoneError(PysleException):
    def __str__(self):
        return "Received an empty phone in the pronunciation list"


class StressedSyllableDetectionError(PysleException):
    def __init__(
        self,
        word: str,
        phoneList: List[str],
        syllableList: List[str],
        islesAdjustedSyllableList: List[str],
    ):
        super(StressedSyllableDetectionError, self).__init__()
        self.word = word
        self.phoneList = phoneList
        self.syllableList = syllableList
        self.islesAdjustedSyllableList = islesAdjustedSyllableList

    def __str__(self):
        return (
            f"\nFor the word '{self.word}' the actual pronunciation was {self.phoneList}\n\n"
            f"this tool attempted to map your phone list with ISLE's syllable list\n"
            f"your mapped syllable list {self.syllableList}\n"
            f"isle's adjusted syllable list {self.islesAdjustedSyllableList}\n\n"
            "This commonly happens due to speech errors--when the speaker adds or removes an entire syllable."
            "You can get around this by \n"
            "    1) adding an entry to the ISLEdict (in alphabetical order) with the "
            "same structure as the actual pronunciation.\n"
            "    2) silencing errors by setting 'stressedSyllableDetectionErrors' to 'ignore' or 'warn'"
        )
