'''
Created on Oct 11, 2012

@author: timmahrt
'''

import io
import re

charList = ['#', '&', '&r', '3r', '9r', '>', '>i', '@', 'A', 'D', 'E',
            'I', 'N', 'S', 'T', 'U', 'Z', '^', 'a', 'aI', 'aU', 'b',
            'd', 'dZ', 'd_(', 'e', 'ei', 'f', 'g', 'h', 'i', 'i:',
            'j', 'k', 'kh', 'l', 'l=', 'm', 'n', 'n=', 'oU', 'p',
            'ph', 'r', 's', 'sh', 't', 'tS', 't_(', 'th', 'u',
            'v', 'w', 'y', 'z']

vowelList = ['a', '@', 'e', 'i', 'o', 'u', '^', '&', '>', ]


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


def search(searchList, matchStr, numSyllables=None, wordInitial='ok',
           wordFinal='ok', spanSyllable='ok', stressedSyllable='ok',
           multiword='ok'):
    '''
    Searches for matching words in the dictionary with regular expressions
    
    wordInitial, wordFinal, spanSyllable, stressSyllable, and multiword
    can take three different values: 'ok', 'only', or 'no'.
    
    Special search characters:
    'V' - any vowel
    'R' - any rhotic
    '#' - word boundary
    'B' - syllable boundary
    '.' - anything
    
    Regular expression syntax applies, so if you wanted to search for any
    word ending with a vowel or rhotic, matchStr = '(?:VR)#'
    '''
    
    # Characters to check between all other characters
    # Don't check between all other characters if the character is already
    # in the search string or
    interleaveStr = None
    stressOpt = (stressedSyllable == 'ok' or stressedSyllable == 'only')
    spanOpt = (spanSyllable == 'ok' or spanSyllable == 'only')
    if stressOpt and spanOpt:
        interleaveStr = "\.?'?"
    elif stressOpt:
        interleaveStr = "'?"
    elif spanOpt:
        interleaveStr = "\.?"
    
    if interleaveStr is not None:
        matchStr = interleaveStr.join(matchStr)
    
    # Setting search boundaries
    # We search on '[^\.#]' and not '.' so that the search doesn't span
    # multiple syllables or words
    if wordInitial == 'only':
        matchStr = '#' + matchStr
    elif wordInitial == 'no':
        # Match the closest preceeding syllable.  If there is none, look
        # for word boundary plus at least one other character
        matchStr = '(?:\.[^\.#]*?|#[^\.#]+?)' + matchStr
    else:
        matchStr = '[#\.][^\.#]*?' + matchStr
    
    if wordFinal == 'only':
        matchStr = matchStr + '#'
    elif wordFinal == 'no':
        matchStr = matchStr + "(?:[^\.#]*?\.|[^\.#]+?#)"
    else:
        matchStr = matchStr + '[^\.#]*?[#\.]'
    
    # Replace special characters
    replDict = {"V": "(?:aI|aU|ei|oU|[AEIaeiu]):?",
                "R": "[&39]?r",
                "B": "\."}
    
    for char, replStr in replDict.items():
        matchStr = matchStr.replace(char, replStr)
    
    # Run search for words
    compiledRE = re.compile(matchStr)
    retList = []
    for word, pronList in searchList:
        newPronList = []
        for pron in pronList:
            searchPron = pron.replace(",", "").replace(" ", "")
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
                    if all(["'" not in match for match in matchList]):
                        continue
                if stressedSyllable == 'no':
                    if all(["'" in match for match in matchList]):
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
            if "'" in phone:
                stressedSyllableList.insert(0, i)
                stressedPhoneList.insert(0, j)
                break
            elif '"' in phone:
                stressedSyllableList.insert(i)
                stressedPhoneList.insert(j)
    
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
