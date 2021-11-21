# encoding: utf-8

from collections import namedtuple
from pkg_resources import resource_filename
from typing import (
    List,
    Tuple,
)
from typing_extensions import Final

ISLE_DOWNLOAD_URL = "https://github.com/uiuc-sst/g2ps/tree/master/English/ISLEdict.txt"

DEFAULT_ISLE_DICT_PATH = resource_filename("pysle", "data/ISLEdict.txt")

Pronunciation: Final[Tuple[str, List[str]]] = namedtuple(
    "Pronunciation", ["pronunciation", "posLabels"]
)

Entry: Final[Tuple[str, List[Pronunciation]]] = namedtuple(
    "Entry", ["word", "pronunciations"]
)

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
