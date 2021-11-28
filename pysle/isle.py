# encoding: utf-8
"""
The main interface for working with the ISLE dictionary.

Can be used to run searches based on written form or
pronunciation ('cat' vs [kat]).

Also has various utility functions.

see
**examples/isletool_examples.py**
**examples/dictionary_search.py**
"""

import copy
import io
import re
import os
from pkg_resources import resource_filename
from typing import List, Optional, Dict, Tuple, Iterable
from typing_extensions import Literal

from pysle.utilities import constants
from pysle.utilities import errors
from pysle.utilities import utils
from pysle.utilities import phonetic_constants
from pysle.utilities import isle_io
from pysle.utilities import search
from pysle import phonetics


def sequenceMatch(matchChar: str, searchStr: str) -> bool:
    """Does marchChar appear in searchStr?"""
    return matchChar in searchStr


class Isle:
    """
    The interface for working with ISLEdict.txt

    Pysle comes with ISLEdict.txt installed but you may specify
    a custom dictionary to search with instead.  Please see README.md
    for more information about obtaining an original copy.
    """

    def __init__(self, islePath: Optional[str] = None):
        if not islePath:
            islePath = constants.DEFAULT_ISLE_DICT_PATH
        elif not os.path.exists(islePath):
            raise errors.IsleDictDoesNotExist()
        else:
            self.data = isle_io.readIsleDict(islePath)

    def getEntries(self) -> Iterable[phonetics.Entry]:
        for word, entries in self.data.items():
            for entry in entries:
                yield entry

    def lookup(self, word: str) -> List[phonetics.Entry]:
        """
        Lookup a word and receive a list of syllables and stressInfo

        Output example for the word 'another' which has two pronunciations
        [
            [Syllabification(syllables=[['ə'], ['n', 'ʌ'], ['ð', 'ɚ']], stressedSyllables=[1], stressedPhones=[1])],
            [Syllabification(syllables=[['ə'], ['n', 'ʌ'], ['ð', 'ə', 'ɹ']], stressedSyllables=[1], stressedPhones=[1])]
        ]
        """
        word = word.lower().strip()

        entries = self.data.get(word, None)

        if entries is None:
            raise errors.WordNotInISLE(word)

        return entries

    def search(
        self,
        matchStr: str,
        numSyllables: Optional[int] = None,
        wordInitial: Literal["ok", "only", "no"] = "ok",
        wordFinal: Literal["ok", "only", "no"] = "ok",
        spanSyllable: Literal["ok", "only", "no"] = "ok",
        stressedSyllable: Literal["ok", "only", "no"] = "ok",
        multiword: Literal["ok", "only", "no"] = "ok",
        pos: Optional[str] = None,
        exactMatch: bool = False,
    ):
        """
        for help on isletool.LexicalTool.search(), see see isletool.search()
        """
        utils.validateOption("wordInitial", wordInitial, constants.AcceptabilityMode)
        utils.validateOption("wordFinal", wordFinal, constants.AcceptabilityMode)
        utils.validateOption("spanSyllable", spanSyllable, constants.AcceptabilityMode)
        utils.validateOption(
            "stressedSyllable", stressedSyllable, constants.AcceptabilityMode
        )
        utils.validateOption("multiword", multiword, constants.AcceptabilityMode)

        return search.search(
            self.data.getEntries(),
            matchStr,
            numSyllables=numSyllables,
            wordInitial=wordInitial,
            wordFinal=wordFinal,
            spanSyllable=spanSyllable,
            stressedSyllable=stressedSyllable,
            multiword=multiword,
            pos=pos,
            exactMatch=exactMatch,
        )

    def getNumPhones(self, word: str, maxFlag: bool) -> Tuple[float, float]:
        """
        Get the number of syllables and phones in this word

        If maxFlag=True, use the longest pronunciation.  Otherwise, take the
        average length.
        """
        phoneCount = 0.0
        syllableCount = 0.0

        syllableCountList = []
        phoneCountList = []

        entryList = self.lookup(word)
        for entry in entryList:
            syllableList = []
            phoneList = []
            for syllabification in entry.syllabificationList:
                syllableList.extend(syllabification.syllables)
                phoneList.extend(syllabification.desyllabify())

            syllableCountList.append(len(syllableList))
            phoneCountList.append(len(phoneList))

        # The average number of phones for all possible pronunciations
        #    of this word
        if maxFlag is True:
            syllableCount += max(syllableCountList)
            phoneCount += max(phoneCountList)
        else:
            syllableCount += sum(syllableCountList) / float(len(syllableCountList))
            phoneCount += sum(phoneCountList) / float(len(phoneCountList))

        return syllableCount, phoneCount

    def contains(self, word: str) -> bool:
        try:
            self.lookup(word)
        except errors.WordNotInISLE:
            return False
        else:
            return True

    def findBestSyllabification(self, word: str, phoneList: List[str]):
        """
        Find the best syllabification for a word

        First find the closest pronunciation to a given pronunciation. Then take
        the syllabification for that pronunciation and map it onto the
        input pronunciation.
        """
        try:
            isleWordList = self.lookup(word)[0]
        except errors.WordNotInISLE:
            # Many words are in the dictionary but not inflected forms
            # like the possesive (eg bob's)
            # If the word could not be found, try dropping the 's
            # and try searching again.
            if len(word) < 2:
                raise

            head = word[:-2]
            tail = word[-2:]
            if tail != "'s":
                raise

            isleWordList = self.lookup(head)

            # Add the 's' sound to each word
            # TODO: don't mutate to avoid deepcopy() call
            modifiedIsleWordList = []
            for entry in isleWordList:
                entry = copy.deepcopy(entry)
                tailSyllabification = entry.syllabificationList[-1]
                finalSyllable = tailSyllabification.syllables[-1]
                lastSound = finalSyllable[-1]

                if lastSound in phonetic_constants.alveolars:
                    finalSyllable.append("ɪ")
                if lastSound in phonetic_constants.unvoiced:
                    finalSyllable.append("s")
                else:
                    finalSyllable.append("z")

                modifiedIsleWordList.append(entry)
            isleWordList = modifiedIsleWordList

        return pronunciationtools._findBestSyllabification(isleWordList, phoneList)

    def findClosestPronunciation(
        self, word: str, phoneList: List[str]
    ) -> phonetics.Syllabification:
        """
        Find the closest dictionary pronunciation to a provided pronunciation
        """
        candidateEntries = self.lookup(word)

        targetEntry = phonetics.Entry("", phoneList, [])
        return pronunciationtools._findBestPronunciation(candidateEntries, targetEntry)[
            0
        ]

    def transcribe(
        self,
        sentenceTxt: str,
        preference: Optional[Literal["longest", "shortest"]] = None,
    ) -> str:
        """
        Can be used to generate a hypothetical pronunciation for a sequence of words

        sentenceTxt is a string with words separated by space e.g. 'Hello world'
        preference is one of None, 'shortest', or 'longest'

        For words with multiple entries in the dictionary, the first entry is chosen
        unless preference is set.  If preference is set to 'longest' or 'shortest' it
        will choose an appropriate pronunciation.  'shortest' is likely a casual
        pronunciation and 'longest' a more formal one.
        """

        if preference:
            utils.validateOption("preference", preference, constants.LengthOptions)

        transcribedWordsList = []
        wordList = sentenceTxt.split(" ")
        for word in wordList:
            entryList = self.lookup(word)

            phoneListsOrderedByEntry = [
                syllabification.desyllabify()
                for entry in entryList
                for syllabification in entry.syllabificationList
            ]
            numPhones = [len(phoneList) for phoneList in phoneListsOrderedByEntry]

            i = 0
            if preference == constants.LengthOptions.SHORTEST:
                i = numPhones.index(min(numPhones))
            elif preference == constants.LengthOptions.LONGEST:
                i = numPhones.index(max(numPhones))

            transcribedWordsList.append(phoneListsOrderedByEntry[i])

        def cleanPron(pron):
            for val in [u"ˈ", u"ˌ", u" "]:
                pron = pron.replace(val, u"")
            return pron

        phoneList = [" ".join(phoneList) for phoneList in transcribedWordsList]
        phoneList = [cleanPron(phones) for phones in phoneList]

        return " ".join(phoneList)


def _sanitizeEntry(entry: phonetics.Entry) -> phonetics.Entry:
    return phonetics.Entry(
        entry[0],
        [
            phonetics.Pronunciation(pronunciation, posList)
            for pronunciation, posList in entry[1]
        ],
    )


def autopair(isleDict: Isle, words: List[str]) -> Tuple[List[List[str]], List[int]]:
    """
    Tests whether adjacent words are OOD or not

    It returns complete wordLists with the matching words replaced.
    Each match yields one sentence.

    e.g.
    red ball chaser
    would return
    [[red_ball chaser], [red ball_chaser]], [0, 1]

    if 'red_ball' and 'ball_chaser' were both in the dictionary
    """

    # Can be '-' or '_'
    newWordList = [
        ("%s_%s" % (words[i], words[i + 1]), i) for i in range(0, len(words) - 1)
    ]

    sentenceList = []
    indexList = []
    for word, i in newWordList:
        if word in isleDict.data:
            sentenceList.append(
                words[:i]
                + [
                    word,
                ]
                + words[i + 2 :]
            )
            indexList.append(i)

    return sentenceList, indexList


def findOODWords(isle: Isle, wordList: List[str]) -> List[str]:
    """
    Returns all of the out-of-dictionary words found in a list of utterances
    """
    oodList = []
    for word in wordList:
        if not isle.contains(word):
            oodList.append(word)

    oodList = list(set(oodList))
    oodList.sort()

    return oodList
