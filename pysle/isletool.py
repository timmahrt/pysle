#encoding: utf-8
'''
The main interface for working with the ISLE dictionary.

Can be used to run searches based on written form or
pronunciation ('cat' vs [kat]).

Also has various utility functions.

see
**examples/isletool_examples.py**
**examples/dictionary_search.py**
'''

import io
import re
import os
import json
from pkg_resources import resource_filename

charList = [u'#', u'.', u'aʊ', u'b', u'd', u'dʒ', u'ei', u'f', u'g',
            u'h', u'i', u'j', u'k', u'l', u'm', u'n', u'oʊ', u'p',
            u'r', u's', u't', u'tʃ', u'u', u'v', u'w', u'z', u'æ',
            u'ð', u'ŋ', u'ɑ', u'ɑɪ', u'ɔ', u'ɔi', u'ə', u'ɚ', u'ɛ', u'ɝ',
            u'ɪ', u'ɵ', u'ɹ', u'ʃ', u'ʊ', u'ʒ', u'æ', u'ʌ', ]

diacriticList = [u'˺', u'ˌ', u'̩', u'̃', u'ˈ', ]

monophthongList = [u'u', u'æ', u'ɑ', u'ɔ', u'ə',
                   u'i', u'ɛ', u'ɪ', u'ʊ', u'ʌ', u'a', u'e', u'o', ]

diphthongList = [u'ɑɪ', u'aʊ', u'ei', u'ɔi', u'oʊ', u'ae']

syllabicConsonantList = [u'l̩', u'n̩', u'ɚ', u'ɝ']

# ISLE words are part of speech tagged using the Penn Part of Speech Tagset
posList = ['cc', 'cd', 'dt', 'fw', 'in', 'jj', 'jjr', 'jjs', 'ls', 'md',
           'nn', 'nnd', 'nnp', 'nnps', 'nns', 'pdt', 'prp', 'punc', 'rb',
           'rbr', 'rbs', 'rp', 'sym', 'to', 'uh', 'vb', 'vbd', 'vbg', 'vbn',
           'vbp', 'vbz', 'vpb', 'wdt', 'wp', 'wrb']

vowelList = monophthongList + diphthongList + syllabicConsonantList

ISLE_DOWNLOAD_URL = 'https://github.com/uiuc-sst/g2ps/tree/master/English/ISLEdict.txt'

DEFAULT_ISLE_DICT_PATH = resource_filename("pysle", "data/ISLEdict.txt")

def isVowel(char):
    '''Is this character a vowel?'''
    return any([vowel in char for vowel in vowelList])


def sequenceMatch(matchChar, searchStr):
    '''Does marchChar appear in searchStr?'''
    return matchChar in searchStr


class WordNotInISLE(Exception):

    def __init__(self, word):
        super(WordNotInISLE, self).__init__()
        self.word = word

    def __str__(self):
        return ("Word '%s' not in ISLE dictionary.  "
                "Please add it to continue." % self.word)


class IsleDictDoesNotExist(Exception):

    def __str__(self):
        return ("You are trying to load a custom ISLE dictionary file that does not exist.\n"
                "By default, the original ISLE dictionary file will be loaded.\n"
                "If you want to use a custom ISLE dictionary, make sure the file exists "
                "and try again with the full path.")


class LexicalTool():
    '''
    The interface for working with ISLEdict.txt

    Requires ISLEdict.txt in order to use.
    Please check isletool.ISLE_DOWNLOAD_URL or the requirements section of the 
    README file for the download location.
    '''

    def __init__(self, islePath=None):
        if not islePath:
            islePath = DEFAULT_ISLE_DICT_PATH
        if not os.path.exists(islePath):
            raise IsleDictDoesNotExist()

        self.data = _readIsleDict(islePath)

    def lookup(self, word):
        '''
        Lookup a word and receive a list of syllables and stressInfo

        Output example for the word 'another' which has two pronunciations
        [(([[u'ə'], [u'n', u'ˈʌ'], [u'ð', u'ɚ']], [1], [1]),
          ([[u'ə'], [u'n', u'ˈʌ'], [u'ð', u'ə', u'ɹ']], [1], [1]))]
        '''

        # All words must be lowercase with no extraneous whitespace
        word = word.lower()
        word = word.strip()

        pronList = self.data.get(word, None)

        if pronList is None:
            raise WordNotInISLE(word)

        pronList = [_parsePronunciation(pronunciationStr)
                    for pronunciationStr, _ in pronList]
        pronList = list(zip(*pronList))

        return pronList

    def search(self, matchStr, numSyllables=None, wordInitial='ok',
               wordFinal='ok', spanSyllable='ok', stressedSyllable='ok',
               multiword='ok', pos=None, exactMatch=False):
        '''
        for help on isletool.LexicalTool.search(), see see isletool.search()
        '''
        return search(self.data.items(), matchStr, numSyllables=numSyllables,
                      wordInitial=wordInitial, wordFinal=wordFinal,
                      spanSyllable=spanSyllable,
                      stressedSyllable=stressedSyllable,
                      multiword=multiword, pos=pos, exactMatch=exactMatch)

def _readIsleDict(islePath):
    '''
    Reads into memory and builds the isle textfile into a dictionary for fast searching
    '''
    lexDict = {}
    with io.open(islePath, "r", encoding='utf-8') as fd:
        for line in fd:
            line = line .rstrip('\n')
            word, pronunciation = line.split(" ", 1)
            word, extraInfo = word.split("(", 1)

            extraInfo = extraInfo.replace(")", "")
            extraInfoList = [segment for segment in extraInfo.split(",")
                             if ("_" not in segment and "+" not in segment and
                                 ':' not in segment and segment != '')]

            lexDict.setdefault(word, [])
            lexDict[word].append((pronunciation, extraInfoList))

    return lexDict

def _prepRESearchStr(matchStr, wordInitial='ok', wordFinal='ok',
                     spanSyllable='ok', stressedSyllable='ok', exactMatch=False):
    '''
    Prepares a user's RE string for a search
    '''

    # Protect sounds that are two characters
    # After this we can assume that each character represents a sound
    # (We'll revert back when we're done processing the RE)
    replList = [(u'ei', u'9'), (u'tʃ', u'='), (u'oʊ', u'~'),
                (u'dʒ', u'@'), (u'aʊ', u'%'), (u'ɑɪ', u'&'),
                (u'ɔi', u'$')]

    # Add to the replList
    currentReplNum = 0
    startI = 0
    for left, right in (('(', ')'), ('[', ']')):
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
    acceptList = ['ok', 'only']
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
    if wordInitial == 'only' or exactMatch:
        matchStr = u'#' + matchStr
    elif wordInitial == 'no':
        # Match the closest preceeding syllable.  If there is none, look
        # for word boundary plus at least one other character
        matchStr = u'(?:\\.[^\\.#]*?|#[^\\.#]+?)' + matchStr
    else:
        matchStr = u'[#\\.][^\\.#]*?' + matchStr

    if wordFinal == 'only' or exactMatch:
        matchStr = matchStr + u'#'
    elif wordFinal == 'no':
        matchStr = matchStr + u"(?:[^\\.#]*?\\.|[^\\.#]+?#)"
    else:
        matchStr = matchStr + u'[^\\.#]*?[#\\.]'

    # For sounds that are designated two characters, prevent
    # detecting those sounds if the user wanted a sound
    # designated by one of the contained characters

    # Forward search ('a' and not 'ab')
    insertList = []
    for charA, charB in [(u'e', u'i'), (u't', u'ʃ'), (u'd', u'ʒ'),
                         (u'o', u'ʊ'), (u'a', u'ʊ|ɪ'), (u'ɔ', u'i'), ]:
        startI = 0
        while True:
            try:
                i = matchStr.index(charA, startI)
            except ValueError:
                break
            if matchStr[i + 1] != charB:
                forwardStr = u'(?!%s)' % charB
#                 matchStr = matchStr[:i + 1] + forwardStr + matchStr[i + 1:]
                startI = i + 1 + len(forwardStr)
                insertList.append((i + 1, forwardStr))

    # Backward search ('b' and not 'ab')
    for charA, charB in [(u't', u'ʃ'), (u'd', u'ʒ'),
                         (u'a|o', u'ʊ'), (u'e|ɔ', u'i'), (u'ɑ', u'ɪ'), ]:
        startI = 0
        while True:
            try:
                i = matchStr.index(charB, startI)
            except ValueError:
                break
            if matchStr[i - 1] != charA:
                backStr = u'(?<!%s)' % charA
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
    replDict = {"D": u"(?:t(?!ʃ)|d(?!ʒ)|[sz])",  # dentals
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


def search(searchList, matchStr, numSyllables=None, wordInitial='ok',
           wordFinal='ok', spanSyllable='ok', stressedSyllable='ok',
           multiword='ok', pos=None, exactMatch=False):
    '''
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
    '''
    # Run search for words

    matchStr = _prepRESearchStr(matchStr, wordInitial, wordFinal,
                                spanSyllable, stressedSyllable, exactMatch)

    compiledRE = re.compile(matchStr)
    retList = []
    for word, pronList in searchList:
        newPronList = []
        for pron, tmpPosList in pronList:
            searchPron = pron.replace(",", "").replace(" ", "")

            # Search for pos
            if pos is not None:
                if pos not in tmpPosList:
                    continue

            # Ignore diacritics for now:
            for diacritic in diacriticList:
                if diacritic not in matchStr:
                    searchPron = searchPron.replace(diacritic, "")

            if numSyllables is not None:
                if numSyllables != searchPron.count('.') + 1:
                    continue

            # Is this a compound word?
            if multiword == 'only':
                if searchPron.count('#') == 2:
                    continue
            elif multiword == 'no':
                if searchPron.count('#') > 2:
                    continue

            matchList = compiledRE.findall(searchPron)
            if len(matchList) > 0:
                if stressedSyllable == 'only':
                    if all([u"ˈ" not in match for match in matchList]):
                        continue
                if stressedSyllable == 'no':
                    if all([u"ˈ" in match for match in matchList]):
                        continue

                # For syllable spanning, we check if there is a syllable
                # marker inside (not at the border) of the match.
                if spanSyllable == 'only':
                    if all(["." not in txt[1:-1] for txt in matchList]):
                        continue
                if spanSyllable == 'no':
                    if all(["." in txt[1:-1] for txt in matchList]):
                        continue
                newPronList.append((pron, tmpPosList))

        if len(newPronList) > 0:
            retList.append((word, newPronList))

    retList.sort()
    return retList


def _parsePronunciation(pronunciationStr):
    '''
    Parses the pronunciation string

    Returns the list of syllables and a list of primary and
    secondary stress locations
    '''
    retList = []
    for syllableTxt in pronunciationStr.split("#"):
        if syllableTxt == "":
            continue
        syllableList = [x.split() for x in syllableTxt.split(' . ')]

        # Find stress
        stressedSyllableList = []
        stressedPhoneList = []
        for i, syllable in enumerate(syllableList):
            for j, phone in enumerate(syllable):
                if u"ˈ" in phone:
                    stressedSyllableList.insert(0, i)
                    stressedPhoneList.insert(0, j)
                    break

                if u'ˌ' in phone:
                    stressedSyllableList.append(i)
                    stressedPhoneList.append(j)

        retList.append((syllableList, stressedSyllableList, stressedPhoneList))

    return retList


def getNumPhones(isleDict, word, maxFlag):
    '''
    Get the number of syllables and phones in this word

    If maxFlag=True, use the longest pronunciation.  Otherwise, take the
    average length.
    '''
    phoneCount = 0
    syllableCount = 0

    syllableCountList = []
    phoneCountList = []

    wordList = isleDict.lookup(word)
    entryList = zip(*wordList)

    for lookupResultList in entryList:
        syllableList = []
        for wordSyllableList in lookupResultList:
            syllableList.extend(wordSyllableList)

        syllableCountList.append(len(syllableList))
        phoneCountList.append(len([phon for phoneList in syllableList for
                                   phon in phoneList]))

    # The average number of phones for all possible pronunciations
    #    of this word
    if maxFlag is True:
        syllableCount += max(syllableCountList)
        phoneCount += max(phoneCountList)
    else:
        syllableCount += (sum(syllableCountList) /
                          float(len(syllableCountList)))
        phoneCount += sum(phoneCountList) / float(len(phoneCountList))

    return syllableCount, phoneCount


def findOODWords(isleDict, wordList):
    '''
    Returns all of the out-of-dictionary words found in a list of utterances
    '''
    oodList = []
    for word in wordList:
        try:
            isleDict.lookup(word)
        except WordNotInISLE:
            oodList.append(word)

    oodList = list(set(oodList))
    oodList.sort()

    return oodList


def transcribe(isleDict, sentenceTxt, preference=None):
    '''
    Can be used to generate a hypothetical pronunciation for a sequence of words

    sentenceTxt is a string with words separated by space e.g. 'Hello world'
    preference is one of None, 'shortest', or 'longest'

    For words with multiple entries in the dictionary, the first entry is chosen
    unless preference is set.  If preference is set to 'longest' or 'shortest' it
    will choose an appropriate pronunciation.  'shortest' is likely a casual
    pronunciation and 'longest' a more formal one.
    '''
    transcribedWordsList = []
    wordList = sentenceTxt.split(" ")
    for word in wordList:
        pronList = isleDict.lookup(word)

        phoneListOfLists = [[phone for syllable in pron[0][0] for phone in syllable]
                            for pron in pronList]
        numPhones = [len(phoneList) for phoneList in phoneListOfLists]

        i = 0
        if preference == 'shortest':
            i = numPhones.index(min(numPhones))
        elif preference == 'longest':
            i = numPhones.index(max(numPhones))

        transcribedWordsList.append(phoneListOfLists[i])

    def cleanPron(pron):
        for val in [u'ˈ', u'ˌ', u' ']:
            pron = pron.replace(val, u'')
        return pron

    phoneList = [" ".join(phoneList) for phoneList in transcribedWordsList]
    phoneList = [cleanPron(phones) for phones in phoneList]

    return " ".join(phoneList)


def autopair(isleDict, wordList):
    '''
    Tests whether adjacent words are OOD or not

    It returns complete wordLists with the matching words replaced.
    Each match yields one sentence.

    e.g.
    red ball chaser
    would return
    [[red_ball chaser], [red ball_chaser]], [0, 1]

    if 'red_ball' and 'ball_chaser' were both in the dictionary
    '''

    newWordList = [("%s_%s" % (wordList[i], wordList[i + 1]), i)
                   for i in range(0, len(wordList) - 1)]

    sentenceList = []
    indexList = []
    for word, i in newWordList:
        if word in isleDict.data:
            sentenceList.append(wordList[:i] + [word, ] + wordList[i + 1:])
            indexList.append(i)

    return sentenceList, indexList
