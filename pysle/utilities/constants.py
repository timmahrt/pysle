# encoding: utf-8

from collections import namedtuple

from typing import (
    List,
    Tuple,
)
from typing_extensions import Final

Syllabification: Final[Tuple[List[List[str]], List[int], List[int]]] = namedtuple(
    "Syllabification", ["syllables", "stressedSyllables", "stressedPhones"]
)


class LengthOptions:
    SHORTEST: Final = "shortest"
    LONGEST: Final = "longest"

    validOptions = [SHORTEST, LONGEST]


class ErrorReportingMode:
    SILENCE: Final = "silence"
    WARNING: Final = "warning"
    ERROR: Final = "error"

    validOptions = [SILENCE, WARNING, ERROR]


class AcceptabilityMode:
    OK: Final = "ok"
    ONLY: Final = "only"
    NO: Final = "no"

    validOptions = [OK, ONLY, NO]
