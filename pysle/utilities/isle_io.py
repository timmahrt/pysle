# encoding: utf-8

import io
from typing import List, Dict, Any

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


def parseIslePronunciation(word, line: str) -> Dict[str, Any]:
    i = line.find("(") + 1
    j = line.find(")", i)
    pos = line[i:j]
    posList = [pos for pos in pos.split(",") if len(pos) <= 3]

    pronunciationInfo = []
    wordStart = line.find("#", j) + 1
    wordEnd = line.find("#", wordStart + 1)
    while wordEnd != -1:
        phonesAsStr = line[wordStart:wordEnd]
        syllables = phonesAsStr.split(".")
        pronunciationInfo.append([syllable.split() for syllable in syllables])
        wordStart = wordEnd + 1
        wordEnd = line.find("#", wordStart + 1)

    return {"word": word, "syllabificationList": pronunciationInfo, "posList": posList}


def getWordFromLine(line: str) -> str:
    i = line.find("(", 0)
    word = line[:i]

    return word


def readIsleDict(islePath: str) -> Dict[str, List[str]]:
    """
    Reads into memory and builds the isle textfile into a dictionary for fast searching
    """
    lexDict: Dict[str, List[str]] = {}
    with io.open(islePath, "r", encoding="utf-8") as fd:
        for line in fd:
            word = getWordFromLine(line)
            lexDict.setdefault(word, [])
            lexDict[word].append(line)

    return lexDict
