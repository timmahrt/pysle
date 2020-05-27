#encoding: utf-8
'''
Created on Oct 22, 2014

@author: tmahrt

Basic examples of common usage.
- looking up words based on their pronunciation
- syllabifying a user-specified phone list based on a pronunciation
  in the dictionary
'''

from os.path import join

from pysle import isletool
from pysle import pronunciationtools

root = join(".", "files")
isleDict = isletool.LexicalTool(join(root, 'ISLEdict_sample.txt'))


# In this first example we look up the syllabification of a word and
# get it's stress information.
searchWord = 'catatonic'
lookupResults = isleDict.lookup(searchWord)

firstEntry = lookupResults[0][0]
firstSyllableList = firstEntry[0]
firstSyllableList = ".".join([u" ".join(syllable)
                              for syllable in firstSyllableList])
firstStressList = firstEntry[1]

print(searchWord)
print(firstSyllableList)
print(firstStressList)  # 3rd syllable carries stress


# In the second example we determine the syllabification of a word,
# as it was said.  (Of course, this is just an estimate)
print('-' * 50)
searchWord = 'another'
anotherPhoneList = ['n', '@', 'th', 'r']
isleWordList = isleDict.lookup(searchWord)
returnList = pronunciationtools.findBestSyllabification(isleDict,
                                                        searchWord,
                                                        anotherPhoneList)

(stressedSyllable, stressedPhone, syllableList, syllabification,
    stressedSyllableIndexList, stressedPhoneIndexList,
    flattenedStressIndexList) = returnList
print(searchWord)
print(anotherPhoneList)
print(stressedSyllableIndexList)  # We can see the first syllable was elided
print(stressedPhoneIndexList)
print(flattenedStressIndexList)
print(syllableList)
print(syllabification)


# In the third example, we have a pronunciation and find the closest dictionary
# pronunciation to it
print('-' * 50)

searchWord = 'labyrinth'
phoneList = ['l', 'a', 'b', 'e', 'r', 'e', 'n', 'th']
isleWordList = isleDict.lookup(searchWord)
retList = pronunciationtools.findClosestPronunciation(isleDict, searchWord, phoneList)
print(searchWord)
print(phoneList)
print(isleWordList)
print(retList)


print('===========================')
searchWord = 'labyrinth'
phoneList = ['l', 'a', 'b', 'e', 'r', 'e', 'n', 'th']
x = pronunciationtools.findBestSyllabification(isleDict,
                                                        searchWord,
                                                        anotherPhoneList)
print(x)

# In the fourth example, we probe what words are in the dictionary
print('-' * 50)

wordList = ["another", "banana", "floplot"]
oodWordList = isletool.findOODWords(isleDict, wordList)
print("The following words are not in the dictionary")
print(oodWordList)


# In the fifth example, we see how many phones are in a pronunciation
print('-' * 50)
syllableCount, phoneCount = isletool.getNumPhones(isleDict,
                                                  "catatonic",
                                                  True)
print("%s: %d phones, %d syllables" % ("catatonic",
                                       phoneCount,
                                       syllableCount))


# In the sixth example, we try to find word pairs in the dictionary
# Once, found, they could be fed into findBestSyllabification() for
# example.
print('-' * 50)
sentenceList = ["another", "australian", "seal", "pumpkins", "parley"]
retList = isletool.autopair(isleDict, sentenceList)[0]
for sentence in retList:
    print(sentence)


# In the seventh example, two pronunciations are aligned.
# This is done by finding the longest common sequence inside of them
# and filling in the gaps before inside and after each string
# so that those common characters appear in the same positions
print('-' * 50)
phoneListA = ['a', 'b', 'c', 'd', 'e', 'f']
phoneListB = ['l', 'a', 'z', 'd', 'u']
alignedPhoneListA, alignedPhoneListB = pronunciationtools.alignPronunciations(phoneListA, phoneListB)
print(alignedPhoneListA)
print(alignedPhoneListB)
