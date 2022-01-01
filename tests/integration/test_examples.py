# encoding: utf-8
"""
Runs user-facing example code

The examples were all written as scripts.  They weren't meant to be
imported or run from other code.  So here, the integration test is just
importing the scripts, which causes them to execute.  If the code completes
with no errors, then the code is at least able to complete.

Testing whether or not the code actually did what it is supposed to is
another issue and will require some refactoring.
"""

import unittest
import os
import sys
from pathlib import Path

from tests.testing_utils import CoverageIgnoredTest

_root = os.path.join(Path(__file__).parents[2], "examples")
sys.path.append(_root)

# Ignoring test coverage because there is no validation in
# these tests other than "no unhandled exception occured"
# which is still important for the user-facing example code
class TestExamples(CoverageIgnoredTest):
    """Ensure example tests run without unhandled exceptions"""

    def test_textgrid_alignment(self):
        """Running 'textgrid_alignment_example.py'"""
        print("\ntextgrid_alignment_example.py" + "\n" + "-" * 10)
        import textgrid_alignment_example

    def test_isletool_examples(self):
        """Running 'isletool_examples.py'"""
        print("\nisletool_examples.py" + "\n" + "-" * 10)
        import isletool_examples

    def test_pronunciationtools_examples(self):
        """Running 'pronunciationtools_examples.py'"""
        print("\npronunciationtools_examples.py" + "\n" + "-" * 10)
        import pronunciationtools_examples

    # def test_dictionary_search(self):
    #     """Running 'dictionary_search.py'"""
    #     print("\ndictionary_search.py" + "\n" + "-" * 10)
    #     import dictionary_search

    def test_syllabify_textgrid(self):
        """Running 'syllabify_textgrid.py'"""
        print("\nsyllabify_textgrid.py" + "\n" + "-" * 10)
        import syllabify_textgrid

    def setUp(self):
        unittest.TestCase.setUp(self)

        root = os.path.join(_root, "files")
        self.oldRoot = os.getcwd()
        os.chdir(_root)
        self.startingList = os.listdir(root)
        self.startingDir = os.getcwd()

    def tearDown(self):
        """Remove any files generated during the test"""
        # unittest.TestCase.tearDown(self)

        root = os.path.join(".", "files")
        endingList = os.listdir(root)
        rmList = [fn for fn in endingList if fn not in self.startingList]

        if self.oldRoot == root:
            for fn in rmList:
                fnFullPath = os.path.join(root, fn)
                if os.path.isdir(fnFullPath):
                    os.rmdir(fnFullPath)
                else:
                    os.remove(fnFullPath)

        os.chdir(self.oldRoot)
