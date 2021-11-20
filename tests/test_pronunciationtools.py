import unittest

from pysle import pronunciationtools


class TestPronunciationtools(unittest.TestCase):
    def test_simplify_pronunciation(self):
        # Assume that phones containing 'r' are rhotics
        self.assertEqual(
            ["r", "r", "r"], pronunciationtools.simplifyPronunciation(["rH", "rr", "r"])
        )
