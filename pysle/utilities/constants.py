# encoding: utf-8

from pkg_resources import resource_filename
from typing_extensions import Final

ISLE_DOWNLOAD_URL = "https://github.com/uiuc-sst/g2ps/tree/master/English/ISLEdict.txt"

DEFAULT_ISLE_DICT_PATH = resource_filename("pysle", "data/ISLEdict.txt")


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
