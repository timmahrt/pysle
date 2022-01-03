# encoding: utf-8
"""High-level functions for working with isle dictionaries

These functions expose an easy-to-use interface that is
otherwise available in different areas of the pysle code
base.
"""

from typing import List, Tuple, Union

from pysle import isletool
from pysle import phonetics


def findBestSyllabification(
    isle: isletool.Isle,
    word: str,
    phoneList: Union[List[str], phonetics.PhonemeList],
) -> phonetics.Syllabification:
    """Find the best syllabification for a phone list

    Args:
        isle: an instance of Isle
        word: the word to lookup
        phoneList: the list of phones for the word

    Returns:
        the best syllabification for the given phone list, using
        the closest pronunciation found in the isle dictionary
    """
    entries = isle.lookup(word)

    phonemes = phonetics._toPhonemeList(phoneList)
    return phonemes.findBestSyllabification(entries)


def findClosestEntryForPhones(
    isle: isletool.Isle,
    word: str,
    phoneList: Union[List[str], phonetics.PhonemeList],
) -> phonetics.Entry:
    """Find the closest entry for a list of phonemes

    Args:
        isle: an instance of Isle
        word: the word to lookup
        phoneList: the list of phones for the word

    Returns:
        the Isle entry with a phone list that is most similar
        to the input one, among the entries for this word
    """
    entries = isle.lookup(word)

    phonemes = phonetics._toPhonemeList(phoneList)
    return phonemes.findClosestEntry(entries)


def findClosestEntryForSyllabification(
    isle: isletool.Isle,
    word: str,
    syllabification: Union[List[List[str]], phonetics.Syllabification],
) -> Tuple[phonetics.Entry, phonetics.Entry]:
    """Find the closest entry for a syllabified list of phonemes

    Args:
        isle: an instance of Isle
        word: the word to lookup
        syllabification: the syllabification for the word

    Returns:
        the Isle entry with a syllabification that is most similar
        to the input one, among the entries for this word
    """
    entries = isle.lookup(word)

    _syllabification = phonetics._toSyllabification(syllabification)
    entry = phonetics.Entry(word, [_syllabification], [])

    return entry.findClosestPronunciation(entries)


def alignPronunciations(
    phoneListA: Union[List[str], phonetics.PhonemeList],
    phoneListB: Union[List[str], phonetics.PhonemeList],
    simplifiedMatching: bool,
) -> Tuple[phonetics.PhonemeList, phonetics.PhonemeList]:
    """Make two lists of phonemes the same length by inserting spaces

    Empty spaces "''" will be inserted around common elements into the two lists.

    Args:
        phoneListA: a list of phones
        phoneListB: a list of phones
        simplifiedMatching: if True, merge all vowels into the symbol "V" and
            all rhotics into the symbol "R", for the purpose of comparing the
            two pronunciations

    Returns:
        the two input phone lists, with spaces inserted
    """
    phonemesA = phonetics._toPhonemeList(phoneListA)
    phonemesB = phonetics._toPhonemeList(phoneListB)

    return phonemesA.align(phonemesB, simplifiedMatching)
