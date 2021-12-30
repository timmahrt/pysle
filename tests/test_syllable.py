import unittest

from pysle import phonetics
from pysle.utilities import errors


class TestSyllable(unittest.TestCase):
    def test_syllable_length(self):
        self.assertTrue(4, len(phonetics.Syllable(["p", "ˈɔ", "ɹ", "k"])))
        self.assertTrue(1, len(phonetics.Syllable(["ˌɑɪ"])))

    def test_has_stress(self):
        self.assertTrue(phonetics.Syllable(["p", "ˈɔ", "ɹ", "k"]).hasStress)
        self.assertFalse(phonetics.Syllable(["j", "ə"]).hasStress)
        self.assertFalse(phonetics.Syllable(["p", "ˌɑɪ", "n", "z"]).hasStress)

    def test_has_secondary_stress(self):
        self.assertFalse(phonetics.Syllable(["p", "ˈɔ", "ɹ", "k"]).hasSecondaryStress)
        self.assertFalse(phonetics.Syllable(["j", "ə"]).hasSecondaryStress)
        self.assertTrue(phonetics.Syllable(["p", "ˌɑɪ", "n", "z"]).hasSecondaryStress)

    def test_nucleus(self):
        self.assertIsNone(phonetics.Syllable(["p", "ɹ", "k"]).nucleus)
        self.assertEqual("ˌɑɪ", phonetics.Syllable(["p", "ˌɑɪ", "n", "z"]).nucleus)

    def test_syllables_cannot_have_more_than_one_vowel(self):
        with self.assertRaises(errors.TooManyVowelsInSyllable) as cm:
            phonetics.Syllable(["m", "a", "ə"])

        self.assertEqual(
            "Error: syllable 'm,a,ə' found to have more than "
            "one vowel.\n This was the CV mapping: 'CVV'",
            str(cm.exception),
        )
