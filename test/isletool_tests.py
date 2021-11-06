import unittest

from pysle import isletool
from pysle import errors


class IsletoolTests(unittest.TestCase):
    def test_transcribe_raises_error_with_invalid_preference(self):
        isleDict = isletool.LexicalTool()

        with self.assertRaises(errors.WrongOption) as _:
            isletool.transcribe(isleDict, "Hello world", preference="fake option")
