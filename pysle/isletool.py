'''
Created on Oct 11, 2012

@author: timmahrt
'''

import io

vowelList = ['a', '@', 'e', 'i', 'o', 'u', '^', '&', '>', ]


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
