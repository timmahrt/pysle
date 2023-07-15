import unittest
from typing import List

from pysle import isletool
from pysle import praattools
from pysle.utilities import errors
from praatio import textgrid

Interval = textgrid.constants.Interval


class VirtualIsle(isletool.Isle):
    def _load(self, _islePath):
        return {
            "cat": ["cat(dt,nn,prp) # k ˌæ t˺ #"],
            "purple": ["purple(jj) # p ˈɝ ɹ . p l̩ #"],
        }


class TestPraattools(unittest.TestCase):
    def setUp(self):
        self.isle = VirtualIsle()

    def assertAlmostAllEqual(self, listA: List[float], listB: List[float]) -> None:
        self.assertEqual(len(listA), len(listB))

        for a, b in zip(listA, listB):
            self.assertAlmostEqual(a, b)
            self.assertAlmostEquals

    def test_spellcheck_textgrid(self):
        tgAsDict = {
            "xmin": 0,
            "xmax": 10,
            "tiers": [
                {
                    "name": "words",
                    "class": "IntervalTier",
                    "xmin": 0,
                    "xmax": 10,
                    "entries": [
                        (0.5, 1.0, "purple"),
                        (1.5, 2.1, "cat"),
                        (3.2, 3.7, "blue"),
                        (4.8, 5.4, "kat"),
                    ],
                }
            ],
        }
        tg = textgrid._dictionaryToTg(tgAsDict, "error")

        sut = praattools.spellCheckTextgrid(
            tg, "words", "words_corrected", self.isle, False
        )

        correctedTier = sut.getTier("words_corrected")

        # All out-of-dictionary words (which could include mispelled words)
        # will be in the output
        self.assertEqual(
            (
                Interval(3.2, 3.7, "blue"),
                Interval(4.8, 5.4, "kat"),
            ),
            correctedTier.entries,
        )

    def test_naive_word_alignment(self):
        tgAsDict = {
            "xmin": 0,
            "xmax": 10,
            "tiers": [
                {
                    "name": "utterances",
                    "class": "IntervalTier",
                    "xmin": 0,
                    "xmax": 10,
                    "entries": [(1.0, 2.0, "purple cat")],
                }
            ],
        }
        tg = textgrid._dictionaryToTg(tgAsDict, "error")

        sut = praattools.naiveWordAlignment(tg, "utterances", "words", self.isle)
        wordTier = sut.getTier("words")

        # There are two words with 7 phones total.  They will divide the 1 second interval
        # into two parts, proportionally.
        boundaryTime = 1 + 5.0 / 8.0
        self.assertEqual(
            (
                Interval(1.0, boundaryTime, "purple"),
                Interval(boundaryTime, 2.0, "cat"),
            ),
            wordTier.entries,
        )

    def test_naive_phone_alignment(self):
        tgAsDict = {
            "xmin": 0,
            "xmax": 10,
            "tiers": [
                {
                    "name": "words",
                    "class": "IntervalTier",
                    "xmin": 0,
                    "xmax": 10,
                    "entries": [
                        (0.5, 1.5, "purple"),
                        (1.5, 2.1, "cat"),
                    ],
                }
            ],
        }
        tg = textgrid._dictionaryToTg(tgAsDict, "error")

        sut = praattools.naivePhoneAlignment(tg, "words", "phones", self.isle)
        phoneTier = sut.getTier("phones")

        self.assertEqual(
            (
                # Purple
                Interval(0.5, 0.7, "p"),
                Interval(0.7, 0.9, "ɝ"),
                Interval(0.9, 1.1, "ɹ"),
                Interval(1.1, 1.3, "p"),
                Interval(1.3, 1.5, "l̩"),
                # Cat
                Interval(1.5, 1.7, "k"),
                Interval(1.7, 1.9, "æ"),
                Interval(1.9, 2.1, "t"),
            ),
            phoneTier.entries,
        )

    def test_syllabify_textgrid(self):
        tgAsDict = {
            "xmin": 0,
            "xmax": 10,
            "tiers": [
                {
                    "name": "words",
                    "class": "IntervalTier",
                    "xmin": 0,
                    "xmax": 10,
                    "entries": [
                        (0.5, 1.5, "purple"),
                        (1.5, 2.1, "cat"),
                    ],
                },
                {
                    "name": "phones",
                    "class": "IntervalTier",
                    "xmin": 0,
                    "xmax": 10,
                    "entries": [
                        # Purple
                        (0.5, 0.75, "p"),
                        (0.75, 1.0, "ɝ"),
                        (1.0, 1.25, "ɹ"),
                        (1.25, 1.3, "p"),
                        (1.3, 1.50, "l"),
                        # Cat
                        (1.5, 1.7, "k"),
                        (1.7, 1.9, "æ"),
                        (1.9, 2.1, "t"),
                    ],
                },
            ],
        }
        tg = textgrid._dictionaryToTg(tgAsDict, "error")

        sut = praattools.syllabifyTextgrid(self.isle, tg, "words", "phones")
        syllableTier = sut.getTier("syllable")

        # Time is divided proportionally
        self.assertEqual(
            (
                # Purple
                Interval(0.5, 1.25, "p-ɝ-ɹ"),
                Interval(1.25, 1.5, "p-l"),
                # Cat
                Interval(1.5, 2.1, "k-æ-t"),
            ),
            syllableTier.entries,
        )

    def test_syllabify_textgrid_raises_error_with_invalid_preference(self):
        tg = textgrid.Textgrid()

        with self.assertRaises(errors.WrongOptionError) as _:
            praattools.syllabifyTextgrid(
                self.isle, tg, "words", "phones", "", stressDetectionErrorMode="bird"
            )
