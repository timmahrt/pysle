import unittest

from pysle import pronunciationtools


class PronunciationtoolsTests(unittest.TestCase):
    def test_simplify_pronunciation(self):
        self.assertEqual(
            ["r", "r", "r"], pronunciationtools.simplifyPronunciation(["rH", "rr", "r"])
        )
