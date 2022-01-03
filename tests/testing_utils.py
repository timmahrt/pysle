import unittest

import pytest


class _DecoratedMethodsClass(type):
    def __new__(cls, name, bases, local):
        for attr in local:
            value = local[attr]
            if callable(value):
                local[attr] = pytest.mark.no_cover(value)  # Ignoring coverage
        return type.__new__(cls, name, bases, local)


# All tests defined in a test that inherits from CoverageIgnoredTest
# will be run but their runs will not be included in test coverage
class CoverageIgnoredTest(unittest.TestCase, metaclass=_DecoratedMethodsClass):
    pass
