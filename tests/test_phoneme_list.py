import unittest
from typing import List

from pysle import phonetics
from pysle.utilities import errors
from pysle.utilities import constants

# For the tests in this file, the word and part of speech information associated
# with an entry don't matter
def entry(phoneList: List[List[List[str]]]):
    return phonetics.Entry("foo", phoneList, ["n"])


class TestPhonemeList(unittest.TestCase):
    def test_equality(self):
        sut = phonetics.PhonemeList(["l", "ˈæ", "b", "ɚ", "ˌɪ", "n", "ɵ"])

        self.assertEqual(
            sut,
            phonetics.PhonemeList(["l", "ˈæ", "b", "ɚ", "ˌɪ", "n", "ɵ"]),
        )

        self.assertNotEqual(
            sut,
            phonetics.PhonemeList(["k", "a", "t"]),
        )
        self.assertNotEqual(sut, 5)

    def test_phoneme_list_length(self):
        self.assertEqual(3, len(phonetics.PhonemeList(["b", "ˈa", "t˺"])))
        self.assertEqual(
            7, len(phonetics.PhonemeList(["b", "i", "r", "d", "c", "a", "k"]))
        )

    def test_phoneme_list_with_empty_string_raises_error(self):
        with self.assertRaises(errors.NullPhoneError) as _:
            phonetics.PhonemeList(["b", "", "t", "i"])

    def test_empty_phone_list(self):
        # TODO: It's not clear what the best behavior should be when the phone list
        #       is empty.
        sut = phonetics.PhonemeList([])

        self.assertEqual([], sut.phonemes)

    def test_adding_phoneme_lists(self):
        phones1 = phonetics.PhonemeList(["b", "i", "r", "d"])
        phones2 = phonetics.PhonemeList(["c", "a", "k"])
        sut = phones1 + phones2

        expectedResult = phonetics.PhonemeList(["b", "i", "r", "d", "c", "a", "k"])
        self.assertEqual(expectedResult, sut)

    def test_strip_diacritics(self):
        phones = phonetics.PhonemeList(["b", "ˈa", "t˺"])
        sut = phones.stripDiacritics()

        expectedResult = phonetics.PhonemeList(["b", "a", "t"])
        self.assertEqual(expectedResult, sut)

    def test_simplify_affects_vowels(self):
        self.assertEqual(
            ["b", "V", "t", "V"],
            phonetics.PhonemeList(["b", "ə", "t", "i"]).simplify().phonemes,
        )

    def test_simplify_affects_rhotics(self):
        self.assertEqual(
            ["r", "r", "r"], phonetics.PhonemeList(["r", "ɾ", "ɹ"]).simplify().phonemes
        )

    def test_simplify_truncates_multicharacter_phonemes(self):
        self.assertEqual(
            ["c", "d", "p"],
            phonetics.PhonemeList(["ch", "dh", "ph"]).simplify().phonemes,
        )

    def test_simplify_removes_diacritics(self):
        self.assertEqual(
            ["r", "p", "t", "n", "n", "v"],
            phonetics.PhonemeList(["r", "ˈp", "t˺", "n̩", "ñ", "ˌv"])
            .simplify()
            .phonemes,
        )

    def test_syllabify_when_phone_length_is_the_same(self):
        sut = phonetics.PhonemeList(["ɪ", "n", "ˈei", "t"])
        syllabification = phonetics.Syllabification([["ə"], ["t", "ˈoʊ", "n"]])
        self.assertEqual(
            [["ɪ"], ["n", "ˈei", "t"]], sut.syllabify(syllabification).toList()
        )

    def test_syllabify_when_syllabification_isolates_consonants(self):
        sut = phonetics.PhonemeList(["f", "r", "ˈei", "t"])
        syllabification = phonetics.Syllabification([["ə"], ["t", "ˈoʊ", "n"]])
        self.assertEqual(
            [["f"], ["r", "ˈei", "t"]], sut.syllabify(syllabification).toList()
        )

    def test_syllabify_when_phoneme_list_is_smaller(self):
        # TODO: Should we potentially throw an error if the phone structure doesn't
        #       match perfectly?
        sut = phonetics.PhonemeList(["r", "ˈai", "t"])
        syllabification = phonetics.Syllabification([["ə"], ["t", "ˈoʊ", "n"]])
        self.assertEqual([["r"], ["ˈai", "t"]], sut.syllabify(syllabification).toList())

    def test_syllabify_drops_syllables_when_phoneme_list_is_much_smaller(self):
        # TODO: Should we enforce that the output of syllabification contains valid
        #       syllables?
        sut = phonetics.PhonemeList(["ˈai", "t"])
        syllabification = phonetics.Syllabification(
            [["ə"], ["t", "ˈoʊ", "n"], ["m", "e", "n", "t"]]
        )
        self.assertEqual([["ˈai"], ["t"]], sut.syllabify(syllabification).toList())

    def test_syllabify_raises_error_when_phoneme_list_is_much_smaller_and_on_size_error_is_error(
        self,
    ):
        sut = phonetics.PhonemeList(["ˈai", "t"])
        syllabification = phonetics.Syllabification(
            [["ə"], ["t", "ˈoʊ", "n"], ["m", "e", "n", "t"]]
        )
        with self.assertRaises(errors.SyllabificationError) as cm:
            sut.syllabify(syllabification, constants.ErrorReportingMode.ERROR)

        self.assertEqual(
            "The target syllabification ([['ə'], ['t', 'ˈoʊ', 'n'], ['m', 'e', 'n', 't']]) "
            "is too long for the input (['ˈai', 't']); the output has been truncated ([['ˈai'], ['t']])",
            str(cm.exception),
        )

    def test_syllabify_drops_syllables_when_phoneme_list_is_much_larger(self):
        sut = phonetics.PhonemeList(["ə", "t", "ˈoʊ", "n", "m", "e", "n", "t"])
        syllabification = phonetics.Syllabification([["ˈai"]])
        self.assertEqual(
            [["ə"]],
            sut.syllabify(syllabification).toList(),
        )

    def test_syllabify_raises_error_when_phoneme_list_is_much_larger_and_on_size_error_is_error(
        self,
    ):
        sut = phonetics.PhonemeList(["ə", "t", "ˈoʊ", "n", "m", "e", "n", "t"])
        syllabification = phonetics.Syllabification([["ˈai"]])
        with self.assertRaises(errors.SyllabificationError) as cm:
            sut.syllabify(syllabification, constants.ErrorReportingMode.ERROR)

        self.assertEqual(
            "The target syllabification ([['ˈai']]) is too short for the input "
            "(['ə', 't', 'ˈoʊ', 'n', 'm', 'e', 'n', 't']); the best fit syllabification output is ([['ə']])",
            str(cm.exception),
        )

    def test_align_with_no_shared_content(self):
        phoneList1 = phonetics.PhonemeList(["a", "b", "c", "d"])
        phoneList2 = phonetics.PhonemeList(["e", "f", "g"])

        phoneList1Aligned, phoneList2Aligned = phoneList1.align(
            phoneList2, simplifiedMatching=False
        )

        self.assertEqual(["a", "b", "c", "d"], phoneList1Aligned.phonemes)
        self.assertEqual(["e", "f", "g", "''"], phoneList2Aligned.phonemes)

    def test_align_with_minimal_match_in_distant_location(self):
        phoneList1 = phonetics.PhonemeList(["a", "b", "c", "d"])
        phoneList2 = phonetics.PhonemeList(["e", "f", "a"])

        phoneList1Aligned, phoneList2Aligned = phoneList1.align(
            phoneList2, simplifiedMatching=False
        )

        self.assertEqual(["''", "''", "a", "b", "c", "d"], phoneList1Aligned.phonemes)
        self.assertEqual(["e", "f", "a", "''", "''", "''"], phoneList2Aligned.phonemes)

    def test_align_with_minimal_match_in_same_location(self):
        phoneList1 = phonetics.PhonemeList(["a", "b", "c", "d"])
        phoneList2 = phonetics.PhonemeList(["a", "f", "g"])

        phoneList1Aligned, phoneList2Aligned = phoneList1.align(
            phoneList2, simplifiedMatching=False
        )

        self.assertEqual(["a", "b", "c", "d"], phoneList1Aligned.phonemes)
        self.assertEqual(["a", "f", "g", "''"], phoneList2Aligned.phonemes)

    def test_align_with_perfect_match(self):
        phoneList1 = phonetics.PhonemeList(["a", "b", "c", "d"])
        phoneList2 = phonetics.PhonemeList(["a", "b", "c", "d"])

        phoneList1Aligned, phoneList2Aligned = phoneList1.align(
            phoneList2, simplifiedMatching=False
        )

        self.assertEqual(["a", "b", "c", "d"], phoneList1Aligned.phonemes)
        self.assertEqual(["a", "b", "c", "d"], phoneList2Aligned.phonemes)

    def test_align_with_match_sequence_seperated_by_filler(self):
        phoneList1 = phonetics.PhonemeList(["z", "a", "b", "c", "f", "d"])
        phoneList2 = phonetics.PhonemeList(["a", "e", "d", "g"])

        phoneList1Aligned, phoneList2Aligned = phoneList1.align(
            phoneList2, simplifiedMatching=False
        )

        self.assertEqual(
            ["z", "a", "b", "c", "f", "d", "''"], phoneList1Aligned.phonemes
        )
        self.assertEqual(
            ["''", "a", "e", "''", "''", "d", "g"], phoneList2Aligned.phonemes
        )

    def test_align_with_match_sequence_separated_by_filler_and_the_sequence_is_the_same_char(
        self,
    ):
        phoneList1 = phonetics.PhonemeList(["z", "a", "b", "c", "f", "a"])
        phoneList2 = phonetics.PhonemeList(["a", "e", "a", "g"])

        phoneList1Aligned, phoneList2Aligned = phoneList1.align(
            phoneList2, simplifiedMatching=False
        )

        self.assertEqual(
            ["z", "a", "b", "c", "f", "a", "''"], phoneList1Aligned.phonemes
        )
        self.assertEqual(
            ["''", "a", "e", "''", "''", "a", "g"], phoneList2Aligned.phonemes
        )

    def test_align_with_match_sequence_seperated_by_filler_when_simplified_matching(
        self,
    ):
        # With simplified matching, all vowels are replaced with the character 'V' for
        # the purpose of matching
        phoneList1 = phonetics.PhonemeList(["z", "a", "b", "c", "f", "a"])
        phoneList2 = phonetics.PhonemeList(["e", "t", "e", "g"])

        phoneList1Aligned, phoneList2Aligned = phoneList1.align(
            phoneList2, simplifiedMatching=True
        )

        self.assertEqual(
            ["z", "a", "b", "c", "f", "a", "''"], phoneList1Aligned.phonemes
        )
        self.assertEqual(
            ["''", "e", "t", "''", "''", "e", "g"], phoneList2Aligned.phonemes
        )

    def test_find_closest_entry_will_pick_out_the_closest_entry(self):
        sut = phonetics.PhonemeList(["p", "ʌ", "m", "k", "n̩"])

        entries = []
        for phoneList in [
            [["p", "ʌ", "m"], ["k", "ɪ", "n"]],
            [["p", "ʌ", "m"], ["k", "n̩"]],
            [["p", "ʌ", "m", "p"], ["k", "n̩"]],
        ]:
            entries.append(entry([phoneList]))

        self.assertEqual(
            entry(
                [
                    [["p", "ʌ", "m"], ["k", "n̩"]],
                ]
            ),
            sut.findClosestEntry(entries),
        )

    def test_find_closest_entry_uses_simplified_forms(self):
        # Vowels and diacritics are ignored
        sut = phonetics.PhonemeList(["p", "ʌ", "m", "k", "n̩"])

        entries = []
        for phoneList in [
            [["p", "ʌ", "m"], ["k", "ɪ", "n"]],
            [["p", "u", "m"], ["k", "n"]],
            [["p", "ʌ", "m"], ["k", "n̩"]],
            [["p", "ʌ", "m", "p"], ["k", "ɪ", "n"]],
        ]:
            entries.append(entry([phoneList]))

        # Although entry 3 is an exact match, entry 2 equally matches
        # the simplified form.  Since it appears first, it is selected
        self.assertEqual(
            entry(
                [
                    [["p", "u", "m"], ["k", "n"]],
                ]
            ),
            sut.findClosestEntry(entries),
        )

    def test_find_closest_entry_prefers_items_with_stress(self):
        # Vowels and diacritics are ignored
        sut = phonetics.PhonemeList(["p", "ʌ", "m", "k", "n̩"])

        entries = []
        for phoneList in [
            [["p", "ʌ", "m"], ["k", "ɪ", "n"]],
            [["p", "u", "m"], ["k", "n"]],
            [["p", "ˈʌ", "m"], ["k", "n̩"]],
            [["p", "ʌ", "m", "p"], ["k", "ɪ", "n"]],
        ]:
            entries.append(entry([phoneList]))

        # Entry 2 and 3 are equally matched, however, entry 3 has
        # stress, so it is selected
        self.assertEqual(
            entry(
                [
                    [["p", "ˈʌ", "m"], ["k", "n̩"]],
                ]
            ),
            sut.findClosestEntry(entries),
        )

    def test_find_closest_entry_fails_for_multi_word_entries(self):
        sut = phonetics.PhonemeList(["p", "ʌ", "m", "k", "n̩", "z"])

        entries = [
            entry(
                [
                    [["p", "ʌ", "m"], ["k", "n̩", "z"]],
                    [["p", "ɑ", "ɹ"], ["l", "i"]],
                ]
            )
        ]

        with self.assertRaises(errors.FeatureNotYetAvailable) as cm:
            sut.findClosestEntry(entries)

        self.assertEqual(
            "findClosestEntry does not support multi-word lookup (yet).  Please file an issue to bump priority.",
            str(cm.exception),
        )

    def test_find_best_syllabification_when_there_is_a_perfect_fit(self):
        # findBestSyllabification combines findClosestEntry and syllabify
        # -- for detailed tests (eg edge cases) it might be better to test
        #    with those two methods?
        sut = phonetics.PhonemeList(["p", "ʌ", "m", "k", "n̩"])

        entries = []
        for phoneList in [
            [["z", "a", "m"], ["k", "ɪ", "n"]],
            [["w", "a", "m"], ["k", "n"]],
            [["l", "a", "m", "p"], ["k", "n"]],
        ]:
            entries.append(entry([phoneList]))

        self.assertEqual(
            [["p", "ʌ", "m"], ["k", "n̩"]],
            sut.findBestSyllabification(entries).toList(),
        )
