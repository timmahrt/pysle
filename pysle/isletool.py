'''
Created on Oct 11, 2012

@author: timmahrt
'''


vowelList = ['a', '@', 'e', 'i', 'o', 'u', '^', '&', '>',]


class WordNotInISLE(Exception):
    
    def __init__(self, word):
        self.word = word
        
    def __str__(self):
        return "Word '%s' not in ISLE dictionary.  Please add it to continue." % self.word



class LexicalTool():
    
    
    def __init__(self, islePath):
        self.islePath = islePath
        self.data = None
        self.pronDict = None
    
    
    def lookup(self, word):
        
        # All words must be lowercase with no extraneous whitespace
        word = word.lower()
        word = word.strip()
        
        # Find indicies in the dictionary
        
        if self.data == None:
            self.data = open(self.islePath, "r").read()
        
        wordList = []
        searchIndex = 0
        while True:
            # (The +1 skips over the "\n" which marks the start of every word)
            startIndex = self.data.find("\n"+word + "(", searchIndex) + 1
            
            # find() returns -1 if it does not find anything, but
            #    note that we added 1 to the return value
            try:
                assert(startIndex != 0)
            except AssertionError:
                if searchIndex == 0:
                    raise WordNotInISLE(word)
                else:
                    break
            
            endIndex = self.data.find("\n", startIndex)
            
            searchIndex = endIndex
            wordList.append((startIndex, endIndex))
            
        returnList = []
        for startIndex, endIndex in wordList:
            isleWord = self.data[startIndex:endIndex]
            syllableTxt = isleWord.split("#")[1].strip()
            syllableList = [x for x in syllableTxt.split(' . ')]
            
            # Find stress
            stressList = []
            for i, syllable in enumerate(syllableList):
                # Primary stress
                if "'" in syllable:
                    stressList.insert(0, i)
                # Secondary stress
                elif '"' in syllable:
                    stressList.append(i)
            
            syllableList = [x.split(" ") for x in syllableList]
            returnList.append((syllableList, stressList))
        
        return returnList


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
        for syllableList, stressIndex in phoneListOfLists:
            syllableCountList.append(len(syllableList))
        
        # In ISLE, there can be multiple pronunciations for each word
        # as we have no reason to believe one pronunciation is more
        # likely than another, we take the average of all of them
        phoneCountList = []
        for syllableList, stressIndex in phoneListOfLists:
            phoneCountList.append(len([phon for phoneList in syllableList for phon in phoneList]))
        
        # The average number of phones for all possible pronunciations
        #    of this word
        if maxFlag == True:
            syllableCount += max(syllableCountList)
            phoneCount += max(phoneCountList)
        else:
            syllableCount += sum(syllableCountList) / float(len(syllableCountList))
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

        
        