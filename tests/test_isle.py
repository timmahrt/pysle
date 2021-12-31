import unittest

from pysle import isle
from pysle import phonetics
from pysle.utilities import errors
from pysle.utilities import constants


class VirtualIsle(isle.Isle):
    def load(self, _islePath):
        return {
            "another": [
                phonetics.Entry(
                    "another",
                    [[["ə"], ["n", "ˈʌ"], ["ð", "ɚ"]]],
                    ["dt", "nn", "prp"],
                ),
                phonetics.Entry(
                    "another",
                    [[["ə"], ["n", "ˈʌ", "ð"], ["ə", "ɹ"]]],
                    ["dt", "nn", "prp"],
                ),
            ],
            "cat": [
                phonetics.Entry(
                    "cat",
                    [[["k", "ˌæ", "t˺"]]],
                    ["dt", "nn", "prp"],
                ),
            ],
            "brown": [
                phonetics.Entry(
                    "brown",
                    [[["b", "ɹ", "ˈaʊ", "n"]]],
                    ["jj"],
                ),
            ],
            "brown_cat": [
                phonetics.Entry(
                    "brown_cat",
                    [[["b", "ɹ", "ˈaʊ", "n"]], [["k", "ˌæ", "t˺"]]],
                    [],
                ),
            ],
        }


class TestIsle(unittest.TestCase):
    def setUp(self):
        self.isle = VirtualIsle()

    def test_lookup(self):
        sut = self.isle.lookup("cat")
        self.assertEqual(1, len(sut))

        self.assertEqual(
            phonetics.Entry(
                "cat",
                [[["k", "ˌæ", "t˺"]]],
                ["dt", "nn", "prp"],
            ),
            sut[0],
        )

    def test_lookup_can_return_multiple_results(self):
        sut = self.isle.lookup("another")
        self.assertEqual(2, len(sut))

        self.assertEqual(
            phonetics.Entry(
                "another",
                [[["ə"], ["n", "ˈʌ"], ["ð", "ɚ"]]],
                ["dt", "nn", "prp"],
            ),
            sut[0],
        )

        self.assertEqual(
            phonetics.Entry(
                "another",
                [[["ə"], ["n", "ˈʌ", "ð"], ["ə", "ɹ"]]],
                ["dt", "nn", "prp"],
            ),
            sut[1],
        )

    def test_get_num_phones_when_get_max_is_false(self):
        # When "getMax" is false, the average number of phones and syllables
        # is used instead
        self.assertEqual((1, 3), self.isle.getNumPhones("cat", False))
        self.assertEqual((3, 5.5), self.isle.getNumPhones("another", False))

    def test_get_num_phones_when_get_max_is_true(self):
        self.assertEqual((1, 3), self.isle.getNumPhones("cat", True))
        self.assertEqual((3, 6), self.isle.getNumPhones("another", True))

    def test_contains(self):
        self.assertEqual(True, self.isle.contains("cat"))
        self.assertEqual(True, self.isle.contains("another"))

        self.assertEqual(False, self.isle.contains("bird"))
        self.assertEqual(False, self.isle.contains("house"))

    def test_find_best_syllabification(self):
        firstMatch = self.isle.findBestSyllabification("another", ["ə", "n", "ˈʌ"])
        self.assertEqual([["ə"], ["n", "ˈʌ"]], firstMatch.toList())

        secondMatch = self.isle.findBestSyllabification(
            "another", ["ə", "n", "ˈʌ", "d", "ɚ"]
        )
        self.assertEqual([["ə"], ["n", "ˈʌ"], ["d", "ɚ"]], secondMatch.toList())

        threeMatch = self.isle.findBestSyllabification(
            "another", ["ə", "n", "ˈʌ", "d", "ə", "ɹ"]
        )
        self.assertEqual([["ə"], ["n", "ˈʌ", "d"], ["ə", "ɹ"]], threeMatch.toList())

    def test_find_closest_pronunciation(self):
        firstMatch = self.isle.findClosestPronunciation("another", ["ə", "n", "ˈʌ"])
        self.assertEqual(["ə", "n", "ˈʌ", "ð", "ɚ"], firstMatch.phonemeList.phonemes)

        secondMatch = self.isle.findClosestPronunciation(
            "another", ["ə", "n", "ˈʌ", "ð", "ə", "r", "r", "r", "r"]
        )
        self.assertEqual(
            ["ə", "n", "ˈʌ", "ð", "ə", "ɹ"], secondMatch.phonemeList.phonemes
        )

    def test_transcribe_raises_error_with_invalid_preference(self):
        with self.assertRaises(errors.WrongOption) as _:
            self.isle.transcribe("Hello world", preference="fake option")

    def test_transcribe_raises_error_for_out_of_dictionary_words(self):
        with self.assertRaises(errors.WordNotInISLE) as _:
            self.assertEqual(True, self.isle.transcribe("Hello world"))

    def test_transcribe_with_no_preference_picks_the_first_option_found(self):
        self.assertEqual("ənʌðɚ kæt˺", self.isle.transcribe("Another cat"))

    def test_transcribe_with_shortest_picks_the_shortest_option(self):
        self.assertEqual(
            "ənʌðɚ kæt˺",
            self.isle.transcribe("Another cat", constants.LengthOptions.SHORTEST),
        )

    def test_transcribe_with_longest_picks_the_longest_option(self):
        self.assertEqual(
            "ənʌðəɹ kæt˺",
            self.isle.transcribe("Another cat", constants.LengthOptions.LONGEST),
        )

    def test_autopair(self):
        self.assertEqual(
            ([["another", "brown_cat", "brown"]], [1]),
            isle.autopair(self.isle, ["another", "brown", "cat", "brown"]),
        )

    def test_autopair_with_multiple_matches(self):
        self.assertEqual(
            (
                [
                    ["another", "brown_cat", "brown", "cat"],
                    ["another", "brown", "cat", "brown_cat"],
                ],
                [1, 3],
            ),
            isle.autopair(self.isle, ["another", "brown", "cat", "brown", "cat"]),
        )

    def test_autopair_with_ood_words_is_ok(self):
        # autopair tests for the presence of word combinations, not individual
        # words
        self.assertEqual(
            ([["brown_cat", "antlion"]], [0]),
            isle.autopair(self.isle, ["brown", "cat", "antlion"]),
        )

    def test_find_ood_words(self):
        self.assertEqual(
            ["antlion", "lazer"],
            isle.findOODWords(self.isle, ["brown", "lazer", "cat", "antlion"]),
        )

    def test_find_ood_words_does_not_return_duplicates(self):
        self.assertEqual(
            ["antlion", "lazer"],
            isle.findOODWords(
                self.isle, ["antlion", "brown", "cat", "antlion", "cat", "lazer"]
            ),
        )
