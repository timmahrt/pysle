#encoding: utf-8
'''
Examples of how to use pysle's regular-expression-based
search functionality.
'''

from os.path import join
import random

from pysle import isletool

root = join('.', 'files')
isleDict = isletool.LexicalTool(join(root, "ISLEdict_sample.txt"))


def printOutMatches(matchStr, numSyllables=None, wordInitial='ok',
                    wordFinal='ok', spanSyllable='ok',
                    stressedSyllable='ok', multiword='ok',
                    numMatches=None, matchList=None, pos=None,
                    exactMatch=False):
    '''Helper function to run searches and output results'''
    if matchList is None:
        matchList = isleDict.search(matchStr, numSyllables, wordInitial,
                                    wordFinal, spanSyllable,
                                    stressedSyllable, multiword, pos, exactMatch)
    else:
        matchList = isletool.search(matchList, matchStr, numSyllables,
                                    wordInitial, wordFinal, spanSyllable,
                                    stressedSyllable, multiword, pos, exactMatch)

    if numMatches is not None and len(matchList) > numMatches:
        random.shuffle(matchList)

    for i, matchTuple in enumerate(matchList):
        if numMatches is not None and i > numMatches:
            break
        word, pronList = matchTuple
        pronList = ["%s(%s)" % (tmpWord, ",".join(posInfo))
                    for tmpWord, posInfo in pronList]
        print("%s: %s" % (word, ",".join(pronList)))
    print("")

    return matchList


# 2-syllable words with a stressed syllable containing 'dV'
# but not word initially
printOutMatches("dV", stressedSyllable="only", spanSyllable="no",
                wordInitial="no", numSyllables=2, numMatches=10)

# 3-syllable word with an 'ld' sequence that spans a syllable boundary
printOutMatches("lBd", wordInitial="no", multiword='no',
                numSyllables=3, numMatches=10, pos="nn")

# words ending in 'inth'
_matchList = printOutMatches(u"ɪnɵ", wordFinal="only", numMatches=10)

# that also start with 's'
printOutMatches("s", wordInitial="only", numMatches=10,
                matchList=_matchList, multiword="no")

# words pronounced exactly as "kæt˺"
printOutMatches("kæt˺", exactMatch=True)

# all words containing "kæt˺"
printOutMatches("kæt˺")
