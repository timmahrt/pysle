#encoding: utf-8
'''
Examples that use the isletool
- looking up words based on their pronunciation
- syllabifying a user-specified phone list based on a pronunciation
  in the dictionary
'''

from os.path import join

from pysle import isletool

# You can specify a custom dictionary to search through.
# By default, the LexicalTool will load the original ISLEdict
root = join(".", "files")
isleDict = isletool.LexicalTool(join(root, 'ISLEdict_sample.txt'))
#isleDict = isletool.LexicalTool()

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


# In the second example, we probe what words are in the dictionary
print('-' * 50)

wordList = ["another", "banana", "floplot"]
oodWordList = isletool.findOODWords(isleDict, wordList)
print("The following words are not in the dictionary")
print(oodWordList)


# In the third example, we see how many phones are in a pronunciation
print('-' * 50)
syllableCount, phoneCount = isletool.getNumPhones(isleDict,
                                                  "catatonic",
                                                  True)
print("%s: %d phones, %d syllables" % ("catatonic",
                                       phoneCount,
                                       syllableCount))


# In the fourth example, we try to find word pairs in the dictionary
# Once, found, they could be fed into findBestSyllabification() for
# example.
print('-' * 50)
sentenceList = ["another", "australian", "seal", "pumpkins", "parley"]
retList = isletool.autopair(isleDict, sentenceList)[0]
for sentence in retList:
    print(sentence)

# In the fifth example, we try to get a pronunciation for a whole
# sentence all at once.
print('-' * 50)
sentence = "do you want another pumpkinseed"
phoneList = isletool.transcribe(isleDict, sentence, 'longest')
print(phoneList)
