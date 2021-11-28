# encoding: utf-8

import io
import re
import os
from pkg_resources import resource_filename
from typing import List, Optional, Dict, Tuple, Iterable
from typing_extensions import Literal

from pysle import phonetics
from pysle.utilities import constants
from pysle.utilities import errors
from pysle.utilities import utils
from pysle.utilities import phonetic_constants


def search(
    searchList: Iterable[phonetics.Entry],
    matchStr: str,
    numSyllables: Optional[int] = None,
    wordInitial: Literal["ok", "only", "no"] = "ok",
    wordFinal: Literal["ok", "only", "no"] = "ok",
    spanSyllable: Literal["ok", "only", "no"] = "ok",
    stressedSyllable: Literal["ok", "only", "no"] = "ok",
    multiword: Literal["ok", "only", "no"] = "ok",
    pos: Optional[str] = None,
    exactMatch: bool = False,
) -> List[phonetics.Entry]:
    """
    Searches for words in searchList that match the pronunciation 'matchStr'

    Internally, uses regular expressions

    wordInitial, wordFinal, spanSyllable, stressedSyllable, and multiword
    can take three different values: 'ok', 'only', or 'no'. For example,
    if spanSyllable is 1) 'ok' then searches will include matches that
    span or do not span syllables.  if 2) 'only', then matches that do
    span syllables are included but matches within syllables are not
    included. if 3) 'no' then matches that span syllables are not
    included but matches within are.

    pos: a tag in the Penn Part of Speech tagset
        see isletool.posList for the full list of possible tags

    exactMatch: match only the exact pronunciation (ignoring stress, syllable markers, etc)

    Special search characters:
    'D' - any dental; 'F' - any fricative; 'S' - any stop
    'V' - any vowel; 'N' - any nasal; 'R' - any rhotic
    '#' - word boundary
    'B' - syllable boundary
    '.' - anything

    For advanced queries:
    Regular expression syntax applies, so if you wanted to search for any
    word ending with a vowel or rhotic, matchStr = '(?:VR)#', '[VR]#', etc.

    Compared with LexicalTool().search(), this function can be used to search through a smaller
    set of data than the entire ISLEdict dictionary.
    """
    utils.validateOption("wordInitial", wordInitial, constants.AcceptabilityMode)
    utils.validateOption("wordFinal", wordFinal, constants.AcceptabilityMode)
    utils.validateOption("spanSyllable", spanSyllable, constants.AcceptabilityMode)
    utils.validateOption(
        "stressedSyllable", stressedSyllable, constants.AcceptabilityMode
    )
    utils.validateOption("multiword", multiword, constants.AcceptabilityMode)

    # Run search for words

    matchStr = _prepRESearchStr(
        matchStr, wordInitial, wordFinal, spanSyllable, stressedSyllable, exactMatch
    )

    compiledRE = re.compile(matchStr)
    retList = []
    for entry in searchList:
        newPronList = []

        searchPron = pronunciation.pronunciation.replace(",", "").replace(" ", "")

        # Search for pos
        if pos is not None:
            if pos not in pronunciation.posLabels:
                continue

        # Ignore diacritics for now:
        for diacritic in phonetic_constants.diacriticList:
            if diacritic not in matchStr:
                searchPron = searchPron.replace(diacritic, "")

        if numSyllables is not None:
            if numSyllables != searchPron.count(".") + 1:
                continue

        # Is this a compound word?
        if multiword == "only":
            if searchPron.count("#") == 2:
                continue
        elif multiword == "no":
            if searchPron.count("#") > 2:
                continue

        matchList = compiledRE.findall(searchPron)
        if len(matchList) > 0:
            if stressedSyllable == "only":
                if all([u"ˈ" not in match for match in matchList]):
                    continue
            if stressedSyllable == "no":
                if all([u"ˈ" in match for match in matchList]):
                    continue

            # For syllable spanning, we check if there is a syllable
            # marker inside (not at the border) of the match.
            if spanSyllable == "only":
                if all(["." not in txt[1:-1] for txt in matchList]):
                    continue
            if spanSyllable == "no":
                if all(["." in txt[1:-1] for txt in matchList]):
                    continue
            newPronList.append(syllabification)

        if len(newPronList) > 0:
            retList.append(phonetics.Entry(entry.word, newPronList, entry.posList))

    retList.sort()
    return retList


def _prepRESearchStr(
    matchStr: str,
    wordInitial: Literal["ok", "only", "no"] = "ok",
    wordFinal: Literal["ok", "only", "no"] = "ok",
    spanSyllable: Literal["ok", "only", "no"] = "ok",
    stressedSyllable: Literal["ok", "only", "no"] = "ok",
    exactMatch: bool = False,
) -> str:
    """
    Prepares a user's RE string for a search
    """

    utils.validateOption("wordInitial", wordInitial, constants.AcceptabilityMode)
    utils.validateOption("wordFinal", wordFinal, constants.AcceptabilityMode)
    utils.validateOption("spanSyllable", spanSyllable, constants.AcceptabilityMode)
    utils.validateOption(
        "stressedSyllable", stressedSyllable, constants.AcceptabilityMode
    )

    # Protect sounds that are two characters
    # After this we can assume that each character represents a sound
    # (We'll revert back when we're done processing the RE)
    replList = [
        (u"ei", u"9"),
        (u"tʃ", u"="),
        (u"oʊ", u"~"),
        (u"dʒ", u"@"),
        (u"aʊ", u"%"),
        (u"ɑɪ", u"&"),
        (u"ɔi", u"$"),
    ]

    # Add to the replList
    currentReplNum = 0
    startI = 0
    for left, right in (("(", ")"), ("[", "]")):
        while True:
            try:
                i = matchStr.index(left, startI)
            except ValueError:
                break
            j = matchStr.index(right, i) + 1
            replList.append((matchStr[i:j], str(currentReplNum)))
            currentReplNum += 1
            startI = j

    for charA, charB in replList:
        matchStr = matchStr.replace(charA, charB)

    # Characters to check between all other characters
    # Don't check between all other characters if the character is already
    # in the search string or
    interleaveStr = None
    acceptList = ["ok", "only"]
    stressOpt = stressedSyllable in acceptList
    spanOpt = spanSyllable in acceptList
    if stressOpt and spanOpt:
        interleaveStr = u"\\.?ˈ?"
    elif stressOpt:
        interleaveStr = u"ˈ?"
    elif spanOpt:
        interleaveStr = u"\\.?"

    if interleaveStr is not None:
        matchStr = interleaveStr.join(matchStr)

    # Setting search boundaries
    # We search on '[^\.#]' and not '.' so that the search doesn't span
    # multiple syllables or words
    if wordInitial == "only" or exactMatch:
        matchStr = u"#" + matchStr
    elif wordInitial == "no":
        # Match the closest preceeding syllable.  If there is none, look
        # for word boundary plus at least one other character
        matchStr = u"(?:\\.[^\\.#]*?|#[^\\.#]+?)" + matchStr
    else:
        matchStr = u"[#\\.][^\\.#]*?" + matchStr

    if wordFinal == "only" or exactMatch:
        matchStr = matchStr + u"#"
    elif wordFinal == "no":
        matchStr = matchStr + u"(?:[^\\.#]*?\\.|[^\\.#]+?#)"
    else:
        matchStr = matchStr + u"[^\\.#]*?[#\\.]"

    # For sounds that are designated two characters, prevent
    # detecting those sounds if the user wanted a sound
    # designated by one of the contained characters

    # Forward search ('a' and not 'ab')
    insertList = []
    for charA, charB in [
        (u"e", u"i"),
        (u"t", u"ʃ"),
        (u"d", u"ʒ"),
        (u"o", u"ʊ"),
        (u"a", u"ʊ|ɪ"),
        (u"ɔ", u"i"),
    ]:
        startI = 0
        while True:
            try:
                i = matchStr.index(charA, startI)
            except ValueError:
                break
            if matchStr[i + 1] != charB:
                forwardStr = u"(?!%s)" % charB
                #                 matchStr = matchStr[:i + 1] + forwardStr + matchStr[i + 1:]
                startI = i + 1 + len(forwardStr)
                insertList.append((i + 1, forwardStr))

    # Backward search ('b' and not 'ab')
    for charA, charB in [
        (u"t", u"ʃ"),
        (u"d", u"ʒ"),
        (u"a|o", u"ʊ"),
        (u"e|ɔ", u"i"),
        (u"ɑ", u"ɪ"),
    ]:
        startI = 0
        while True:
            try:
                i = matchStr.index(charB, startI)
            except ValueError:
                break
            if matchStr[i - 1] != charA:
                backStr = u"(?<!%s)" % charA
                #                 matchStr = matchStr[:i] + backStr + matchStr[i:]
                startI = i + 1 + len(backStr)
                insertList.append((i, backStr))

    insertList.sort()
    for i, insertStr in insertList[::-1]:
        matchStr = matchStr[:i] + insertStr + matchStr[i:]

    # Revert the special sounds back from 1 character to 2 characters
    for charA, charB in replList:
        matchStr = matchStr.replace(charB, charA)

    # Replace special characters
    replDict = {
        "D": u"(?:t(?!ʃ)|d(?!ʒ)|[sz])",  # dentals
        "F": u"[ʃʒfvszɵðh]",  # fricatives
        "S": u"(?:t(?!ʃ)|d(?!ʒ)|[pbkg])",  # stops
        "N": u"[nmŋ]",  # nasals
        "R": u"[rɝɚ]",  # rhotics
        "V": u"(?:aʊ|ei|oʊ|ɑɪ|ɔi|[iuæɑɔəɛɪʊʌ]):?",  # vowels
        "B": u"\\.",  # syllable boundary
    }

    for char, replStr in replDict.items():
        matchStr = matchStr.replace(char, replStr)

    if exactMatch:
        matchStr = "^" + matchStr + "$"

    return matchStr
