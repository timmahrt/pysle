import unittest

from pysle import isle
from pysle import praattools
from pysle.utilities import errors
from praatio import textgrid


class TestPraattools(unittest.TestCase):
    def test_syllabify_textgrid_raises_error_with_invalid_preference(self):
        isleDict = isle.Isle()
        tg = textgrid.Textgrid()

        with self.assertRaises(errors.WrongOption) as _:
            praattools.syllabifyTextgrid(
                isleDict, tg, "words", "phones", "", stressDetectionErrorMode="bird"
            )
