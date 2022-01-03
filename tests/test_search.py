import unittest
from typing import List

from pysle import phonetics
from pysle import isletool
from pysle import praattools
from pysle.utilities import errors


class VirtualIsle(isletool.Isle):
    def _load(self, _islePath):
        return {
            "another": [
                "another(dt,nn,prp) # ə . n ˈʌ . ð ɚ #",
                "another(dt,nn,prp) # ə . n ˈʌ ð . ə ɹ #",
            ],
            "any": ["any(dt) # ˈɛ . n i #"],
            "brown": ["brown(jj) # b ɹ ˈaʊ n #"],
            "brown_cat": ["brown_cat() # b ɹ ˈaʊ n # k ˌæ t˺ #"],
            "cat": ["cat(dt,nn,prp) # k ˌæ t˺ #"],
            "nominee": ["nominee(nn) # n ˌɑ . m ə . n ˈi #"],
        }


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.isle = VirtualIsle()

    def test_num_syllables(self):
        results = [result for result in self.isle.search("VNV", numSyllables=None)]
        self.assertEqual(4, len(results))
        self.assertEqual("another", results[0]["word"])
        self.assertEqual("another", results[1]["word"])
        self.assertEqual("any", results[2]["word"])
        self.assertEqual("nominee", results[3]["word"])

        results = [result for result in self.isle.search("VNV", numSyllables=1)]
        self.assertEqual(0, len(results))

        results = [result for result in self.isle.search("VNV", numSyllables=2)]
        self.assertEqual(1, len(results))
        self.assertEqual("any", results[0]["word"])

        results = [result for result in self.isle.search("VNV", numSyllables=3)]
        self.assertEqual(3, len(results))
        self.assertEqual("another", results[0]["word"])
        self.assertEqual("another", results[1]["word"])
        self.assertEqual("nominee", results[2]["word"])

    def test_word_initial(self):
        results = [result for result in self.isle.search("NV", wordInitial="ok")]
        self.assertEqual(4, len(results))
        self.assertEqual("another", results[0]["word"])
        self.assertEqual("another", results[1]["word"])
        self.assertEqual("any", results[2]["word"])
        self.assertEqual("nominee", results[3]["word"])

        results = [result for result in self.isle.search("NV", wordInitial="no")]
        self.assertEqual(4, len(results))
        self.assertEqual("another", results[0]["word"])
        self.assertEqual("another", results[1]["word"])
        self.assertEqual("any", results[2]["word"])
        self.assertEqual("nominee", results[3]["word"])  # b/c the second 'n'

        results = [result for result in self.isle.search("NV", wordInitial="only")]
        self.assertEqual(1, len(results))
        self.assertEqual("nominee", results[0]["word"])

    def test_word_final(self):
        results = [result for result in self.isle.search("ɹ", wordFinal="ok")]
        self.assertEqual(3, len(results))
        self.assertEqual("another", results[0]["word"])
        self.assertEqual("brown", results[1]["word"])
        self.assertEqual("brown_cat", results[2]["word"])

        results = [result for result in self.isle.search("ɹ", wordFinal="no")]
        self.assertEqual(2, len(results))
        self.assertEqual("brown", results[0]["word"])
        self.assertEqual("brown_cat", results[1]["word"])

        results = [result for result in self.isle.search("ɹ", wordFinal="only")]
        self.assertEqual(1, len(results))
        self.assertEqual("another", results[0]["word"])

    def test_span_syllable(self):
        results = [result for result in self.isle.search("VD", spanSyllable="ok")]
        self.assertEqual(4, len(results))
        self.assertEqual("another", results[0]["word"])
        self.assertEqual("another", results[1]["word"])
        self.assertEqual("brown_cat", results[2]["word"])
        self.assertEqual("cat", results[3]["word"])

        results = [result for result in self.isle.search("VD", spanSyllable="no")]
        self.assertEqual(3, len(results))
        self.assertEqual("another", results[0]["word"])
        self.assertEqual("brown_cat", results[1]["word"])
        self.assertEqual("cat", results[2]["word"])

        results = [result for result in self.isle.search("VD", spanSyllable="only")]
        self.assertEqual(1, len(results))
        self.assertEqual("another", results[0]["word"])

    def test_stressed_syllable(self):
        results = [result for result in self.isle.search("Ni", stressedSyllable="ok")]
        self.assertEqual(2, len(results))
        self.assertEqual("any", results[0]["word"])
        self.assertEqual("nominee", results[1]["word"])

        results = [result for result in self.isle.search("Ni", stressedSyllable="only")]
        self.assertEqual(1, len(results))
        self.assertEqual("nominee", results[0]["word"])

        results = [result for result in self.isle.search("Ni", stressedSyllable="no")]
        self.assertEqual(1, len(results))
        self.assertEqual("any", results[0]["word"])

    def test_multiword(self):
        results = [result for result in self.isle.search("kV", multiword="ok")]

        self.assertEqual(2, len(results))
        self.assertEqual("brown_cat", results[0]["word"])
        self.assertEqual("cat", results[1]["word"])

        results = [result for result in self.isle.search("kV", multiword="only")]

        self.assertEqual(1, len(results))
        self.assertEqual("brown_cat", results[0]["word"])

        results = [result for result in self.isle.search("kV", multiword="no")]

        self.assertEqual(1, len(results))
        self.assertEqual("cat", results[0]["word"])

    def test_pos(self):
        results = [result for result in self.isle.search("Vt", pos=None)]

        self.assertEqual(2, len(results))
        self.assertEqual(("brown_cat", ""), (results[0]["word"], results[0]["posList"]))
        self.assertEqual(
            ("cat", "dt,nn,prp"), (results[1]["word"], results[1]["posList"])
        )

        results = [result for result in self.isle.search("Vt", pos="nn")]

        self.assertEqual(1, len(results))
        self.assertEqual(
            ("cat", "dt,nn,prp"), (results[0]["word"], results[0]["posList"])
        )

    def test_exact_match(self):
        results = [result for result in self.isle.search("bɹaʊn", exactMatch=False)]

        self.assertEqual(2, len(results))
        self.assertEqual("brown", results[0]["word"])
        self.assertEqual("brown_cat", results[1]["word"])

        results = [result for result in self.isle.search("bɹaʊn", exactMatch=True)]

        self.assertEqual(1, len(results))
        self.assertEqual("brown", results[0]["word"])
