# encoding: utf-8
"""The main interface for working with the ISLE dictionary."""

import copy
import os
from typing import List, Optional, Tuple, Iterable, Union, Dict, Generator
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
    """The interface for working with ISLEdict.txt

    Pysle comes with ISLEdict.txt installed but you may specify
    a custom dictionary to search with instead.  Please see README.md
    for more information about obtaining an original copy.
    """

    def __init__(self, islePath: Optional[str] = None):
        """The constructor for isle

        Creating an instance of Isle() will load Isle into memory
        which can take time.

        Args:
            islePath: the path to an islex dictionary.  If None, the
                original islex will be used.
        """
        if not islePath:
            islePath = constants.DEFAULT_ISLE_DICT_PATH
        elif not os.path.exists(islePath):
            raise errors.IsleDictDoesNotExistError()

        self.rawData = self._load(islePath)
        self.data: Dict[str, List[phonetics.Entry]] = {}

    def _load(self, islePath) -> Dict[str, List[str]]:
        print("Text")
        return isle_io.readIsleDict(islePath)

    def _lazyLoad(self, word: str) -> List[phonetics.Entry]:
        """Fetches entries for a word; if not parsed yet, parses the original text"""

        entries = self.data.get(word)
        if not entries:
            lazyLoadedEntries: List[phonetics.Entry] = []

            lines = self.rawData.get(word)
            if lines is None:
                raise errors.WordNotInIsleError(word)

            for rawIsleLine in lines:
                entryAsHash = isle_io.parseIslePronunciation(word, rawIsleLine)
                entry = phonetics.Entry(
                    entryAsHash["word"],
                    entryAsHash["syllabificationList"],
                    entryAsHash["posList"],
                )
                lazyLoadedEntries.append(entry)

            self.data[word] = lazyLoadedEntries
            return lazyLoadedEntries
        else:
            return entries

    def getEntries(self) -> Iterable[phonetics.Entry]:
        """Iterates through the isle dictionary

        Yields:
            individual entries in alphabetical order
        """
        for word in self.rawData.keys():
            for entry in self._lazyLoad(word):
                yield entry

    def lookup(self, word: str) -> List[phonetics.Entry]:
        """
        Lookup a word and receive a list of syllables and stressInfo

        Output example for the word 'another' which has two pronunciations
        [
            [Syllabification(syllables=[['ə'], ['n', 'ʌ'], ['ð', 'ɚ']], stressedSyllables=[1], stressedPhones=[1])],
            [Syllabification(syllables=[['ə'], ['n', 'ʌ'], ['ð', 'ə', 'ɹ']], stressedSyllables=[1], stressedPhones=[1])]
        ]

        Args:
            word: the word to lookup

        Returns:
            A list of entries; each entry is unique for a word, pronunciation pair

        Raises:
            WordNotInIsleError: The word was not in the Isle dictionary
        """
        word = word.lower().strip()

        return self._lazyLoad(word)

    def getLength(self, word: str, maxFlag: bool) -> Tuple[float, float]:
        """
        Get the number of syllables and phones in this word

        Args:
            word: the word to lookup
            maxFlag: if True, use the longest pronunciation of all matching entries.
                If False, use the average length

        Returns:
            a tuple containing the number of syllables and number of phones
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
                phoneList.extend(syllabification.desyllabify().phonemes)

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
        """Check if a word exists in the isle dictionary"""
        try:
            self.lookup(word)
        except errors.WordNotInIsleError:
            return False
        else:
            return True

    def findBestSyllabification(
        self, word: str, phoneList: Union[phonetics.PhonemeList, List[str]]
    ) -> phonetics.Syllabification:
        """
        Find the best syllabification for a word

        First find the closest pronunciation to a given pronunciation. Then take
        the syllabification for that pronunciation and map it onto the
        input pronunciation.

        Args:
            word: the word to lookup
            phoneList: the phonemes to syllabify

        Returns:
            a syllabified version of the input phoneList

        Raises:
            WordNotInIsleError: The word was not in the Isle dictionary
        """
        phoneList = phonetics._toPhonemeList(phoneList)

        try:
            entries = self.lookup(word)
        except errors.WordNotInIsleError:
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

            entries = self.lookup(head)

            # Add the 's' sound to each word
            # TODO: don't mutate to avoid deepcopy() call
            modifiedIsleWordList = []
            for entry in entries:
                entry = copy.deepcopy(entry)
                tailSyllabification = entry.syllabificationList[-1]
                finalSyllable = tailSyllabification.syllables[-1]
                lastSound = finalSyllable.phonemes[-1]

                if lastSound in phonetic_constants.alveolars:
                    finalSyllable.phonemes.append("ɪ")
                if lastSound in phonetic_constants.unvoiced:
                    finalSyllable.phonemes.append("s")
                else:
                    finalSyllable.phonemes.append("z")

                modifiedIsleWordList.append(entry)
            entries = modifiedIsleWordList

        return phoneList.findBestSyllabification(entries)

    def findClosestPronunciation(
        self, word: str, phoneList: Union[phonetics.PhonemeList, List[str]]
    ) -> phonetics.Entry:
        """
        Find the closest dictionary pronunciation to a provided pronunciation
        """
        phoneList = phonetics._toPhonemeList(phoneList)
        candidateEntries = self.lookup(word)

        return phoneList.findClosestEntry(candidateEntries)

    def transcribe(
        self,
        sentenceTxt: str,
        preference: Optional[Literal["longest", "shortest"]] = None,
    ) -> str:
        """
        Can be used to generate a hypothetical pronunciation for a sequence of words

        Args:
            sentenceTxt: a sequence of words separated by space e.g. 'Hello world'
            preference: if 'shortest', or 'longest', the appropriate option will be
                picked (based on phone length); otherwise, the first option will
                be picked

        Returns:
            a sequence of IPA characters, separated by space for each word
            e.g. 'hɛloʊ wɜrld'
        """

        if preference:
            utils.validateOption("preference", preference, constants.LengthOptions)

        transcribedWordsList: List[phonetics.PhonemeList] = []
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

        words: List[str] = [
            " ".join(phoneList.phonemes) for phoneList in transcribedWordsList
        ]
        words = [cleanPron(phones) for phones in words]

        return " ".join(words)

    def search(
        self,
        searchString: str,
        numSyllables: Optional[int] = None,
        wordInitial: Literal["ok", "only", "no"] = "ok",
        wordFinal: Literal["ok", "only", "no"] = "ok",
        spanSyllable: Literal["ok", "only", "no"] = "ok",
        stressedSyllable: Literal["ok", "only", "no"] = "ok",
        multiword: Literal["ok", "only", "no"] = "ok",
        pos: Optional[str] = None,
        exactMatch: bool = False,
        randomize: bool = False,
    ) -> Generator[Dict[str, str], None, None]:
        """Search for isledict entries based on pronunciation

        wordInitial, wordFinal, spanSyllable, stressedSyllable, and multiword
        can take three different values: 'ok', 'only', or 'no'. For example,
        if spanSyllable is 1) 'ok' then searches will include matches that
        span or do not span syllables.  if 2) 'only', then matches that do
        span syllables are included but matches within syllables are not
        included. if 3) 'no' then matches that span syllables are not
        included but matches within are.

        Special search characters:
        'D' - any dental; 'F' - any fricative; 'S' - any stop
        'V' - any vowel; 'N' - any nasal; 'R' - any rhotic
        '#' - word boundary
        'B' - syllable boundary
        '.' - anything

        For example, 'DV.' would search for the three character:
        'dental, vowel, anything'

        For advanced queries:
        Regular expression syntax applies, so if you wanted to search for any
        word ending with a vowel or rhotic, matchStr = '(?:VR)#', '[VR]#', etc.

        Args:
            searchString: the text to search for
            numSyllables: return results with the given number of syllables
            wordInitial: return matches that occur in word-initial position
            wordFinal: return matches that occur in word-final position
            spanSyllable: return matches that span across syllables
            stressedSyllable: return matches that are in stressed position
            multiword: return matches that are composed of multiple words
            pos: a tag in the Penn Part of Speech tagset
                see isletool.phonetics.posList for the full list of possible tags
            exactMatch: match only the exact pronunciation (ignoring stress,
                 syllable markers, etc)
            randomize: randomize the search order (useful if you are only looking for
                a few results)

        Returns:
            a generator for iterating through results

        """

        # Prep the data for searching
        wordInfoList = []
        for word, lines in self.rawData.items():
            for line in lines:
                posStart = line.find("(")
                posEnd = line.find(")", posStart)
                wordStart = line.find("#", posEnd)

                posList = line[posStart + 1 : posEnd]
                wordInfoList.append(
                    {
                        "word": word,
                        "posList": posList,
                        "pronunciation": line[wordStart:],
                    }
                )

        for matchedWordInfo in search.search(
            wordInfoList,
            searchString,
            numSyllables,
            wordInitial,
            wordFinal,
            spanSyllable,
            stressedSyllable,
            multiword,
            pos,
            exactMatch,
            randomize,
        ):
            yield matchedWordInfo


def autopair(isle: Isle, words: List[str]) -> Tuple[List[List[str]], List[int]]:
    """
    Joins adjacent words, if their combination is in the

    It returns complete wordLists with the matching words replaced.
    Each match yields one sentence.

    e.g. (assuming 'red_ball' and 'ball_chaser' are both in isle)
    ```python
    x = ['red', 'ball', 'chaser']
    print(autopair(isle, x))
    >> [['red_ball', 'chaser'], ['red', 'ball_chaser']], [0, 1]
    ```

    Args:
        isle: an instance of Isle
        words: a list of words

    Returns:
        a list of potential matching sentences and a corresponding list of indicies,
        where each index is the starting word where the match was found
    """

    # TODO: Is this method unnecessarily complex?  Maybe we can just return a list
    #       of all adjacent pairs that are in isle?
    # TODO: Can be '-' or '_'
    newWordList = [
        ("%s_%s" % (words[i], words[i + 1]), i) for i in range(0, len(words) - 1)
    ]

    sentenceList = []
    indexList = []
    for word, i in newWordList:
        if word in isle.rawData:
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
    Returns all of the unique out-of-dictionary words found in a list
    """
    oodList = []
    for word in wordList:
        if not isle.contains(word):
            oodList.append(word)

    oodList = list(set(oodList))
    oodList.sort()

    return oodList
