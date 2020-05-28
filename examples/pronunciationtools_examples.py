#encoding: utf-8
'''
Examples of how to use pysle's pronunciationtools code
'''

from os.path import join

from pysle import isletool
from pysle import pronunciationtools

root = join(".", "files")
isleDict = isletool.LexicalTool(join(root, 'ISLEdict_sample.txt'))

# In the first example we determine the syllabification of a word,
# as it was said.  (Of course, this is just an estimate)
print('-' * 50)
searchWord = 'another'
anotherPhoneList = ['n', '@', 'th', 'r']
isleWordList = isleDict.lookup(searchWord)
returnList = pronunciationtools.findBestSyllabification(
    isleDict, searchWord, anotherPhoneList)

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


# In the second example, we have a pronunciation and find the closest dictionary
# pronunciation to it
print('-' * 50)

searchWord = 'labyrinth'
phoneList = ['l', 'a', 'b', 'e', 'r', 'e', 'n', 'th']
isleWordList = isleDict.lookup(searchWord)
retList = pronunciationtools.findClosestPronunciation(
    isleDict, searchWord, phoneList)
print(searchWord)
print(phoneList)
print(isleWordList)
print(retList)

print('===========================')
searchWord = 'labyrinth'
phoneList = ['l', 'a', 'b', 'e', 'r', 'e', 'n', 'th']
x = pronunciationtools.findBestSyllabification(
    isleDict, searchWord, anotherPhoneList)
print(x)


# In the third example, two pronunciations are aligned.
# This is done by finding the longest common sequence inside of them
# and filling in the gaps before inside and after each string
# so that those common characters appear in the same positions
print('-' * 50)
phoneListA = ['a', 'b', 'c', 'd', 'e', 'f']
phoneListB = ['l', 'a', 'z', 'd', 'u']
alignedPhoneListA, alignedPhoneListB = pronunciationtools.alignPronunciations(
    phoneListA, phoneListB)
print(alignedPhoneListA)
print(alignedPhoneListB)
