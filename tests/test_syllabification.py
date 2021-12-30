import unittest
from typing import List

from pysle import phonetics


def syllabification(
    syllables: List[List[str]] = None,
    stressedSyllables: List[int] = None,
    stressedVowels: List[int] = None,
):
    syllables = [["k", "a", "t"]] if syllables is None else syllables
    stressedSyllables = [] if stressedSyllables is None else stressedSyllables
    stressedVowels = [] if stressedVowels is None else stressedVowels

    return phonetics.Syllabification(syllables, stressedSyllables, stressedVowels)


class TestSyllabification(unittest.TestCase):
    def test_syllabification_length(self):
        self.assertEqual(
            1,
            len(
                syllabification(
                    syllables=[["k", "ˈa", "t"]],
                    stressedSyllables=[0],
                    stressedVowels=[1],
                )
            ),
        )
        self.assertEqual(
            3,
            len(
                syllabification(
                    syllables=[["l", "ˈæ"], ["b", "ɚ"], ["ˌɪ", "n", "ɵ"]],
                    stressedSyllables=[0],
                    stressedVowels=[1],
                )
            ),
        )

    def test_has_stress(self):
        self.assertEqual(
            True,
            syllabification(
                syllables=[["k", "ˈa", "t"]], stressedSyllables=[0], stressedVowels=[1]
            ).hasStress,
        )

        self.assertEqual(
            False,
            syllabification(
                syllables=[["k", "a", "t"]], stressedSyllables=[], stressedVowels=[]
            ).hasStress,
        )

    def test_stress(self):
        self.assertEqual(
            [
                0,
                2,
            ],
            syllabification(
                syllables=[["l", "ˈæ"], ["b", "ɚ"], ["ˌɪ", "n", "ɵ"]],
                stressedSyllables=[0],
                stressedVowels=[1],
            ).stress,
        )

        self.assertEqual(
            [],
            syllabification(
                syllables=[["l", "æ"], ["b", "ɚ"], ["ɪ", "n", "ɵ"]],
                stressedSyllables=[],
                stressedVowels=[],
            ).stress,
        )

    def test_to_list(self):
        self.assertEqual(
            [["l", "ˈæ"], ["b", "ɚ"], ["ˌɪ", "n", "ɵ"]],
            syllabification(
                syllables=[["l", "ˈæ"], ["b", "ɚ"], ["ˌɪ", "n", "ɵ"]],
            ).toList(),
        )

    def test_desyllabify(self):
        self.assertEqual(
            phonetics.PhonemeList(["l", "ˈæ", "b", "ɚ", "ˌɪ", "n", "ɵ"]),
            syllabification(
                syllables=[["l", "ˈæ"], ["b", "ɚ"], ["ˌɪ", "n", "ɵ"]],
            ).desyllabify(),
        )

    def test_morph_first_syllable_initial_pos(self):
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification([["b", "p", "m"], ["k", "n"]])
        self.assertEqual(
            [["''", "p", "m"], ["k", "n"]],
            sut.morph(targetSyllabification).toList(),
        )

    def test_morph_first_syllable_medial_pos(self):
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification([["p", "ʌ", "m"], ["k", "n"]])
        self.assertEqual(
            [["p", "''", "m"], ["k", "n"]],
            sut.morph(targetSyllabification).toList(),
        )

    def test_morph_first_syllable_final_pos(self):
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification([["p", "m", "p"], ["k", "n"]])
        self.assertEqual(
            [["p", "m", "''"], ["k", "n"]],
            sut.morph(targetSyllabification).toList(),
        )

    def test_morph_non_first_syllable_medial_pos(self):
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification([["p", "m"], ["k", "ɪ", "n"]])
        self.assertEqual(
            [["p", "m"], ["k", "''", "n"]],
            sut.morph(targetSyllabification).toList(),
        )

    def test_morph_non_first_syllable_final_pos(self):
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification([["p", "m"], ["k", "n", "z"]])
        self.assertEqual(
            [["p", "m"], ["k", "n", "''"]],
            sut.morph(targetSyllabification).toList(),
        )

    def test_morph_non_first_syllable_initial_pos(self):
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification([["p", "m"], ["p", "k", "n"]])
        self.assertEqual(
            [["p", "m"], ["''", "k", "n"]],
            sut.morph(targetSyllabification).toList(),
        )

    def test_morph_multiple_insertions_on_one_syllable(self):
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification(
            [["t", "b", "p", "m"], ["k", "n"]]
        )
        self.assertEqual(
            [["''", "''", "p", "m"], ["k", "n"]],
            sut.morph(targetSyllabification).toList(),
        )
