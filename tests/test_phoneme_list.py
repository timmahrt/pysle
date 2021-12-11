import unittest

from pysle import phonetics


class TestPhonemeList(unittest.TestCase):
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

    def test_simplify(self):
        pass

    def test_syllabify(self):
        pass

    def test_align(self):
        pass
