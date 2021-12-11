import unittest

from pysle import isle
from pysle.utilities import errors


class TestIsle(unittest.TestCase):
    def test_transcribe_raises_error_with_invalid_preference(self):
        isleDict = isle.Isle()

        with self.assertRaises(errors.WrongOption) as _:
            isleDict.transcribe("Hello world", preference="fake option")
