import unittest

from pysle import phonetics


class TestPhonetics(unittest.TestCase):
    def test_is_vowel_for_vowels(self):
        for vowel in ["a", "e", "i", "o", "u"]:
            self.assertTrue(phonetics.isVowel(vowel))

    def test_is_vowel_for_nonvowels(self):
        for nonvowel in ["k", "v", "1", "'", "B"]:
            self.assertFalse(phonetics.isVowel(nonvowel))
