# encoding: utf-8

import io
from typing import List, Dict

from pysle import phonetics


def _parsePronunciation(
    pronunciationStr: str,
) -> List[phonetics.Syllabification]:
    """
    Parses the pronunciation string

    Returns the list of syllables and a list of primary and
    secondary stress locations--one for each word (entries
    can have multiple words eg "weather balloon")
    """

    syllabificationList = []
    for syllablesTxt in pronunciationStr.split("#"):
        if syllablesTxt == "":
            continue
        syllables = [
            [phone for phone in syllableTxt.strip().split()]
            for syllableTxt in syllablesTxt.split(" . ")
        ]

        syllabificationList.append(phonetics.Syllabification.new(syllables))

    return syllabificationList


def _parsePosInfo(posInfoStr: str):
    return [
        segment
        for segment in posInfoStr.replace(")", "").split(",")
        if (all([char not in segment for char in ["_", "+", ":"]]) and segment != "")
    ]


def parseIsleLine(line: str) -> phonetics.Entry:
    line = line.rstrip("\n")
    prefix, pronunciationInfoText = line.split(" ", 1)
    word, posInfoText = prefix.split("(", 1)

    syllabificationList = _parsePronunciation(pronunciationInfoText)
    posList = _parsePosInfo(posInfoText)

    return phonetics.Entry(word, syllabificationList, posList)


def readIsleDict(islePath: str) -> Dict[str, List[phonetics.Entry]]:
    """
    Reads into memory and builds the isle textfile into a dictionary for fast searching
    """
    lexDict: Dict[str, List[phonetics.Entry]] = {}
    with io.open(islePath, "r", encoding="utf-8") as fd:
        for line in fd:
            entry = parseIsleLine(line)
            lexDict.setdefault(entry.word, [])
            lexDict[entry.word].append(entry)

    return lexDict
