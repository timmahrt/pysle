# encoding: utf-8
"""
Examples of how to use pysle's pronunciationtools code
"""

from os.path import join

from pysle import isle
from pysle import phonetics
from pysle import pronunciationtools

root = join(".", "files")
isleDict = isle.Isle(join(root, "ISLEdict_sample.txt"))

# In the first example we determine the syllabification of a word,
# as it was said.  (Of course, this is just an estimate)
print("-" * 50)
searchWord = "another"
anotherPhoneList = ["n", "@", "th", "r"]
entries = isleDict.lookup(searchWord)
syllabification = pronunciationtools.findBestSyllabification(
    isleDict, searchWord, anotherPhoneList
)
closestEntry = pronunciationtools.findClosestEntryForPhones(
    isleDict, searchWord, anotherPhoneList
)

print(syllabification.toList())
print(closestEntry.toList())

# In the second example, we have a pronunciation and find the closest dictionary
# pronunciation to it
print("-" * 50)

searchWord = "labyrinth"
labrinthSyllables = [
    ["l", "a"],
    ["b", "e", "r"],
    ["e", "n", "th"],
]

closestEntry, constructedEntry = pronunciationtools.findClosestEntryForSyllabification(
    isleDict, searchWord, labrinthSyllables
)
print("---------------")
print(searchWord)
print(labrinthSyllables)
print(closestEntry.toList())
print(constructedEntry.toList())

print("===========================")
searchWord = "labyrinth"
labrinthPhones = ["l", "a", "b", "e", "r", "e", "n", "th"]
labrinthSyllabification = pronunciationtools.findBestSyllabification(
    isleDict, searchWord, labrinthPhones
)
print(labrinthSyllabification.toList())


# In the third example, two pronunciations are aligned.
# This is done by finding the longest common sequence inside of them
# and filling in the gaps before inside and after each string
# so that those common characters appear in the same positions
print("-" * 50)
phoneListA = ["a", "b", "c", "d", "e", "f"]
phoneListB = ["l", "a", "z", "d", "u"]

alignedPhoneListA, alignedPhoneListB = pronunciationtools.alignPronunciations(
    phoneListA, phoneListB, True
)
print(alignedPhoneListA.phonemes)
print(alignedPhoneListB.phonemes)
