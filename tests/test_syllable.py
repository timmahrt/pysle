import unittest

from pysle import phonetics


class TestSyllable(unittest.TestCase):
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
