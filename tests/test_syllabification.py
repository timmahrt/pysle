import unittest
from typing import List

from pysle import phonetics
from pysle.utilities import errors


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
    def test_equality(self):
        sut = phonetics.Syllabification.new([["l", "ˈæ"], ["b", "ɚ"], ["ˌɪ", "n", "ɵ"]])

        self.assertEqual(
            sut,
            phonetics.Syllabification.new([["l", "ˈæ"], ["b", "ɚ"], ["ˌɪ", "n", "ɵ"]]),
        )

        self.assertNotEqual(
            sut,
            phonetics.Syllabification.new([["k", "a", "t"]]),
        )
        self.assertNotEqual(sut, 5)

    def test_new_will_determine_stress_location(self):
        sut = phonetics.Syllabification.new([["l", "ˈæ"], ["b", "ɚ"], ["ˌɪ", "n", "ɵ"]])
        expectedSyllabification = phonetics.Syllabification(
            [["l", "ˈæ"], ["b", "ɚ"], ["ˌɪ", "n", "ɵ"]], [0, 2], [1, 0]
        )

        self.assertEqual(sut, expectedSyllabification)

    def test_new_can_take_a_list_of_syllables(self):
        syllableList = []
        for syllable in [["l", "ˈæ"], ["b", "ɚ"], ["ˌɪ", "n", "ɵ"]]:
            syllableList.append(phonetics.Syllable(syllable))

        sut = phonetics.Syllabification.new(syllableList)
        expectedSyllabification = phonetics.Syllabification(
            [["l", "ˈæ"], ["b", "ɚ"], ["ˌɪ", "n", "ɵ"]], [0, 2], [1, 0]
        )

        self.assertEqual(sut, expectedSyllabification)

    def test_new_throws_exception_if_input_is_malformed(self):
        with self.assertRaises(AttributeError) as cm:
            sut = phonetics.Syllabification.new(["l", "ˈæ"])

    def test_syllabification_instance_if_input_is_malformed(self):
        with self.assertRaises(AttributeError) as cm:
            sut = phonetics.Syllabification(["l", "ˈæ"])

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
            [0, 2],
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

    def test_stretch_first_syllable_initial_pos(self):
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification([["b", "p", "m"], ["k", "n"]])
        self.assertEqual(
            [["''", "p", "m"], ["k", "n"]],
            sut.stretch(targetSyllabification).toList(),
        )

    def test_stretch_first_syllable_medial_pos(self):
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification([["p", "ʌ", "m"], ["k", "n"]])
        self.assertEqual(
            [["p", "''", "m"], ["k", "n"]],
            sut.stretch(targetSyllabification).toList(),
        )

    def test_stretch_first_syllable_final_pos(self):
        # TODO: The intuition from the user is that the first syllable should be stretched
        #       but actually its the second syllable.
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification([["p", "m", "p"], ["k", "n"]])
        self.assertEqual(
            [["p", "m"], ["''", "k", "n"]],
            sut.stretch(targetSyllabification).toList(),
        )

    def test_stretch_non_first_syllable_medial_pos(self):
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification([["p", "m"], ["k", "ɪ", "n"]])
        self.assertEqual(
            [["p", "m"], ["k", "''", "n"]],
            sut.stretch(targetSyllabification).toList(),
        )

    def test_stretch_non_first_syllable_final_pos(self):
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification([["p", "m"], ["k", "n", "z"]])
        self.assertEqual(
            [["p", "m"], ["k", "n", "''"]],
            sut.stretch(targetSyllabification).toList(),
        )

    def test_stretch_non_first_syllable_initial_pos(self):
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification([["p", "m"], ["p", "k", "n"]])
        self.assertEqual(
            [["p", "m"], ["''", "k", "n"]],
            sut.stretch(targetSyllabification).toList(),
        )

    def test_stretch_multiple_insertions_on_one_syllable(self):
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification(
            [["t", "b", "p", "m"], ["k", "n"]]
        )
        self.assertEqual(
            [["''", "''", "p", "m"], ["k", "n"]],
            sut.stretch(targetSyllabification).toList(),
        )

    def test_stretch_when_syllable_structure_differs(self):
        # Morph considers only the flattened phone list, so the target's
        # syllable structure doesn't matter
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification(
            [["t", "b"], ["p", "m"], ["k", "n"]]
        )
        self.assertEqual(
            [["''", "''", "p", "m"], ["k", "n"]],
            sut.stretch(targetSyllabification).toList(),
        )

    def test_stretch_results_are_meaningless_if_target_alignment_is_poor(
        self,
    ):
        # Source's final syllable matches with the target's first syllable
        sut = phonetics.Syllabification([["p", "m"], ["k", "n"]])
        targetSyllabification = phonetics.Syllabification(
            [["k", "n"], ["z", "v"], ["j", "l"]]
        )

        self.assertEqual(
            [["p", "m"], ["k", "n", "''", "''", "''", "''"]],
            sut.stretch(targetSyllabification).toList(),
        )

    def test_stretch_results_are_meaningless_if_the_targets_syllable_structure_is_very_different(
        self,
    ):
        sut = phonetics.Syllabification([["t", "b"], ["p", "m"]])
        targetSyllabification = phonetics.Syllabification(
            [["a", "t", "b", "v"], ["j", "p", "m", "k"]]
        )

        self.assertEqual(
            [["''", "t", "b"], ["''", "''", "p", "m", "''"]],
            sut.stretch(targetSyllabification).toList(),
        )
