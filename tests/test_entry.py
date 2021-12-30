import unittest
from typing import List

from pysle import phonetics


def entry(
    name: str = "bird",
    phoneList: List[List[List[str]]] = None,
    posList: List[str] = None,
):
    phoneList = [[["b", "r", "d"]]] if phoneList is None else phoneList
    posList = ["n"] if posList is None else posList

    return phonetics.Entry(name, phoneList, posList)


class TestEntry(unittest.TestCase):
    def test_has_stress_for_single_syllable_words(self):
        self.assertEqual(False, entry(phoneList=[[["f", "a", "r"]]]).hasStress)
        self.assertEqual(True, entry(phoneList=[[["f", "ˈa", "r"]]]).hasStress)

    def test_has_stress_for_multiple_syllable_words(self):
        self.assertEqual(False, entry(phoneList=[[["ɪ"], ["n", "ei", "t"]]]).hasStress)
        self.assertEqual(True, entry(phoneList=[[["ɪ"], ["n", "ˈei", "t"]]]).hasStress)
        self.assertEqual(
            True,
            entry(phoneList=[[["l", "ˈæ"], ["b", "ɚ"], ["ˌɪ", "n", "ɵ"]]]).hasStress,
        )

    def test_has_stress_for_multiple_word_entries(self):
        # a) no stress marks
        self.assertEqual(
            False,
            entry(
                phoneList=[
                    [["p", "ʌ", "m"], ["k", "n̩", "z"]],
                    [["p", "ɑ", "ɹ"], ["l", "i"]],
                ]
            ).hasStress,
        )
        # b) stress mark in first word
        self.assertEqual(
            True,
            entry(
                phoneList=[
                    [["p", "ʌ", "m"], ["k", "ˈn̩", "z"]],
                    [["p", "ɑ", "ɹ"], ["l", "i"]],
                ]
            ).hasStress,
        )
        # c) stress mark in second word
        self.assertEqual(
            True,
            entry(
                phoneList=[
                    [["p", "ʌ", "m"], ["k", "n̩", "z"]],
                    [["p", "ˈɑ", "ɹ"], ["l", "i"]],
                ]
            ).hasStress,
        )

    def test_phoneme_list_for_single_syllable_words(self):
        self.assertEqual(
            ["f", "a", "r"], entry(phoneList=[[["f", "a", "r"]]]).phonemeList.phonemes
        )

    def test_phoneme_list_with_words_with_stress(self):
        self.assertEqual(
            ["f", "ˈa", "r"], entry(phoneList=[[["f", "ˈa", "r"]]]).phonemeList.phonemes
        )

    def test_phoneme_list_for_multiple_syllable_words(self):
        self.assertEqual(
            ["l", "ˈæ", "b", "ɚ", "ˌɪ", "n", "ɵ"],
            entry(
                phoneList=[[["l", "ˈæ"], ["b", "ɚ"], ["ˌɪ", "n", "ɵ"]]]
            ).phonemeList.phonemes,
        )

    def test_phoneme_list_for_multiple_word_entries(self):
        self.assertEqual(
            ["p", "ʌ", "m", "k", "n̩", "z", "p", "ˈɑ", "ɹ", "l", "i"],
            entry(
                phoneList=[
                    [["p", "ʌ", "m"], ["k", "n̩", "z"]],
                    [["p", "ˈɑ", "ɹ"], ["l", "i"]],
                ]
            ).phonemeList.phonemes,
        )

    def test_to_list(self):
        self.assertEqual(
            [
                [["p", "ʌ", "m"], ["k", "n̩", "z"]],
                [["p", "ˈɑ", "ɹ"], ["l", "i"]],
            ],
            entry(
                phoneList=[
                    [["p", "ʌ", "m"], ["k", "n̩", "z"]],
                    [["p", "ˈɑ", "ɹ"], ["l", "i"]],
                ]
            ).toList(),
        )

    def test_find_closest_pronunciation(self):
        pass
