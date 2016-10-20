#encoding: utf-8
'''
Created on Oct 11, 2012

@author: timmahrt
'''

import io
import re


charList = [u'#', u'.', u'aʊ', u'b', u'd', u'dʒ', u'ei', u'f', u'g',
            u'h', u'i', u'j', u'k', u'l', u'm', u'n', u'oʊ', u'p',
            u'r', u's', u't', u'tʃ', u'u', u'v', u'w', u'z', u'æ',
            u'ð', u'ŋ', u'ɑ', u'ɑɪ', u'ɔ', u'ɔi', u'ə', u'ɚ', u'ɛ', u'ɝ',
            u'ɪ', u'ɵ', u'ɹ', u'ʃ', u'ʊ', u'ʒ', u'æ', u'ʌ', ]

diacriticList = [u'˺', u'ˌ', u'̩', u'̃', ]

vowelList = [u'aʊ', u'ei', u'i', u'oʊ', u'u', u'æ',
             u'ɑ', u'ɑɪ', u'ɔ', u'ɔi', u'ə', u'ɚ', u'ɛ', u'ɝ',
             u'ɪ', u'ʊ', u'ʌ', ]


def isVowel(char):
    return any([vowel in char for vowel in vowelList])


def sequenceMatch(matchChar, searchStr):
    return matchChar in searchStr


class WordNotInISLE(Exception):
    
    def __init__(self, word):
        super(WordNotInISLE, self).__init__()
        self.word = word
        
    def __str__(self):
        return ("Word '%s' not in ISLE dictionary.  "
                "Please add it to continue." % self.word)


class LexicalTool():
    
    def __init__(self, islePath):
        self.islePath = islePath
        self.data = self._buildDict()
    
    def _buildDict(self):
        '''
        Builds the isle textfile into a dictionary for fast searching
        '''
        lexDict = {}
        with io.open(self.islePath, "r", encoding='utf-8') as fd:
            wordList = [line.rstrip('\n') for line in fd]
            
        for row in wordList:
            word, pronunciation = row.split(" ", 1)
            word = word.split("(")[0]
            
            lexDict.setdefault(word, [])
            lexDict[word].append(pronunciation)
        
        return lexDict
    
    def lookup(self, word):
        '''
        Lookup a word and receive a list of syllables and stressInfo
        '''
        
        # All words must be lowercase with no extraneous whitespace
        word = word.lower()
        word = word.strip()
        
        pronList = self.data.get(word, None)
        
        if pronList is None:
            raise WordNotInISLE(word)
        else:
            pronList = [_parsePronunciation(pronunciationStr)
                        for pronunciationStr in pronList]
        
        return pronList

    def search(self, matchStr, numSyllables=None, wordInitial='ok',
               wordFinal='ok', spanSyllable='ok', stressedSyllable='ok',
               multiword='ok'):
        return search(self.data.items(), matchStr, numSyllables=numSyllables,
                      wordInitial=wordInitial, wordFinal=wordFinal,
                      spanSyllable=spanSyllable,
                      stressedSyllable=stressedSyllable,
                      multiword=multiword)


def _prepRESearchStr(matchStr, wordInitial='ok', wordFinal='ok',
                     spanSyllable='ok', stressedSyllable='ok'):
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
    stressOpt = (stressedSyllable == 'ok' or stressedSyllable == 'only')
    spanOpt = (spanSyllable == 'ok' or spanSyllable == 'only')
    if stressOpt and spanOpt:
        interleaveStr = u"\.?ˈ?"
    elif stressOpt:
        interleaveStr = u"ˈ?"
    elif spanOpt:
        interleaveStr = u"\.?"
    
    if interleaveStr is not None:
        matchStr = interleaveStr.join(matchStr)
    
    # Setting search boundaries
    # We search on '[^\.#]' and not '.' so that the search doesn't span
    # multiple syllables or words
    if wordInitial == 'only':
        matchStr = u'#' + matchStr
    elif wordInitial == 'no':
        # Match the closest preceeding syllable.  If there is none, look
        # for word boundary plus at least one other character
        matchStr = u'(?:\.[^\.#]*?|#[^\.#]+?)' + matchStr
    else:
        matchStr = u'[#\.][^\.#]*?' + matchStr
    
    if wordFinal == 'only':
        matchStr = matchStr + u'#'
    elif wordFinal == 'no':
        matchStr = matchStr + u"(?:[^\.#]*?\.|[^\.#]+?#)"
    else:
        matchStr = matchStr + u'[^\.#]*?[#\.]'
    
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
                         (u'a|o', u'ʊ'), (u'e|ɔ', u'i'), (u'ɑ' u'ɪ'), ]:
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
                "B": u"\.",  # syllable boundary
                }

    for char, replStr in replDict.items():
        matchStr = matchStr.replace(char, replStr)

    return matchStr


def search(searchList, matchStr, numSyllables=None, wordInitial='ok',
           wordFinal='ok', spanSyllable='ok', stressedSyllable='ok',
           multiword='ok'):
    '''
    Searches for matching words in the dictionary with regular expressions
    
    wordInitial, wordFinal, spanSyllable, stressSyllable, and multiword
    can take three different values: 'ok', 'only', or 'no'.
    
    Special search characters:
    'D' - any dental; 'F' - any fricative; 'S' - any stop
    'V' - any vowel; 'N' - any nasal; 'R' - any rhotic
    '#' - word boundary
    'B' - syllable boundary
    '.' - anything
    
    For advanced queries:
    Regular expression syntax applies, so if you wanted to search for any
    word ending with a vowel or rhotic, matchStr = '(?:VR)#', '[VR]#', etc.
    '''
    # Run search for words
    
    matchStr = _prepRESearchStr(matchStr, wordInitial, wordFinal,
                                spanSyllable, stressedSyllable)
    
    compiledRE = re.compile(matchStr)
    retList = []
    for word, pronList in searchList:
        newPronList = []
        for pron in pronList:
            searchPron = pron.replace(",", "").replace(" ", "")
            
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
                newPronList.append(pron)
        
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
    syllableTxt = pronunciationStr.split("#")[1].strip()
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
            elif u'ˌ' in phone:
                stressedSyllableList.append(i)
                stressedPhoneList.append(j)
    
    return syllableList, stressedSyllableList, stressedPhoneList
            
            
def getNumPhones(isleDict, label, maxFlag):
    '''
    
    If maxFlag=True, use the longest pronunciation.  Otherwise, take the
    average length.
    '''
    phoneCount = 0
    syllableCount = 0
    for word in label.split():

        phoneListOfLists = isleDict.lookup(word)
        
        syllableCountList = []
        for row in phoneListOfLists:
            syllableList = row[0]
            syllableCountList.append(len(syllableList))
        
        # In ISLE, there can be multiple pronunciations for each word
        # as we have no reason to believe one pronunciation is more
        # likely than another, we take the average of all of them
        phoneCountList = []
        for row in phoneListOfLists:
            syllableList = row[0]
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
