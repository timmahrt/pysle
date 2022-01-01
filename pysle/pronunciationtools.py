# encoding: utf-8

from typing import List, Tuple, Union

from pysle import isle
from pysle import phonetics


def findBestSyllabification(
    isleDict: isle.Isle,
    word: str,
    phoneList: Union[List[str], phonetics.PhonemeList],
) -> phonetics.Syllabification:
    """
    Find the best syllabification for a phone list
    """
    entries = isleDict.lookup(word)

    phonemes = phonetics._toPhonemeList(phoneList)
    return phonemes.findBestSyllabification(entries)


def findClosestEntryForPhones(
    isleDict: isle.Isle,
    word: str,
    phoneList: Union[List[str], phonetics.PhonemeList],
) -> phonetics.Entry:
    """
    Find the closest entry for a list of phonemes
    """
    entries = isleDict.lookup(word)

    phonemes = phonetics._toPhonemeList(phoneList)
    return phonemes.findClosestEntry(entries)


def findClosestEntryForSyllabification(
    isleDict: isle.Isle,
    word: str,
    syllabification: Union[List[List[str]], phonetics.Syllabification],
) -> Tuple[phonetics.Entry, phonetics.Entry]:
    """
    Find the closest entry for a syllabified list of phonemes
    """
    entries = isleDict.lookup(word)

    _syllabification = phonetics._toSyllabification(syllabification)
    entry = phonetics.Entry(word, [_syllabification], [])

    return entry.findClosestPronunciation(entries)


def alignPronunciations(
    phoneListA: Union[List[str], phonetics.PhonemeList],
    phoneListB: Union[List[str], phonetics.PhonemeList],
    simplifiedMatching: bool,
) -> Tuple[phonetics.PhonemeList, phonetics.PhonemeList]:
    """
    Make two lists of phonemes the same length by inserting spaces

    Spaces will be inserted around common elements into the two lists.
    """
    phonemesA = phonetics._toPhonemeList(phoneListA)
    phonemesB = phonetics._toPhonemeList(phoneListB)

    return phonemesA.align(phonemesB, simplifiedMatching)
