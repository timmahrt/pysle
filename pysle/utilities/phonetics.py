# encoding: utf-8

import io
import re
import os
from pkg_resources import resource_filename
from typing import (
    List,
    Optional,
    Dict,
    Tuple,
)
from typing_extensions import Literal

from pysle.utilities import errors
from pysle.utilities import phonetic_constants
from pysle.utilities import isle_io


def isVowel(char: str) -> bool:
    """Is this character a vowel?"""
    return any([vowel in char for vowel in phonetic_constants.vowelList])


class PhonemeList(object):
    def __init__(self, phonemes: str):
        self.phonemes = phonemes

    def simplify(self):
        """
        Simplifies pronunciation

        Removes diacritics and unifies vowels and rhotics
        """
        simplifiedPhones = []
        for phone in self.phonemes:

            # Remove diacritics
            for diacritic in phonetic_constants.diacriticList:
                phone = phone.replace(diacritic, "")

            # Unify rhotics
            if "r" in phone:
                phone = "r"

            phone = phone.lower()

            # Unify vowels
            if isVowel(phone):
                phone = "V"

            # Only represent the string by its first letter
            try:
                phone = phone[0]
            except IndexError:
                raise errors.NullPhoneError()

            # Unify vowels (reducing the vowel to one char)
            if isVowel(phone):
                phone = "V"

            simplifiedPhones.append(phone)

        return simplifiedPhones


class Pronunciation(object):
    def __init__(self, pronunciation, posList: List[str]):
        self.pronunciation = pronunciation
        self.posList = posList


class Syllabification(object):
    def __init__(
        self,
        syllables: List[PhonemeList],
        stressedSyllableIndicies: List[int],
        stressedVowelIndicies: List[int],
    ):
        self.syllables = syllables
        self.stressedSyllableIndicies = stressedSyllableIndicies
        self.stressedVowelIndicies = stressedVowelIndicies

    def desyllabify(self):
        return [phone for entry in self.syllables for phone in entry.pronunciation]


class Entry(object):
    def __init__(
        self, word: str, syllabificationList: List[Syllabification], posList: List[str]
    ):
        self.word = word
        self.syllabificationList = syllabificationList
        self.posList = posList
