#encoding: utf-8
'''
Created on July 08, 2016

@author: tmahrt

Basic examples of common usage.
'''

import random

from pysle import isletool

tmpPath = r"C:\Users\Tim\Dropbox\workspace\pysle\test\ISLEdict.txt"
isleDict = isletool.LexicalTool(tmpPath)

def printOutMatches(matchStr, numSyllables=None, wordInitial='ok',
                    wordFinal='ok', spanSyllable='ok', stressedSyllable='ok',
                    multiword='ok', numMatches=None, matchList=None):

    if matchList is None:
        matchList = isleDict.search(matchStr, numSyllables, wordInitial,
                                    wordFinal, spanSyllable, stressedSyllable,
                                    multiword)
    else:
        matchList = isletool.search(matchList, matchStr, numSyllables, wordInitial,
                                    wordFinal, spanSyllable, stressedSyllable,
                                    multiword)
    
    if numMatches is not None and len(matchList) > numMatches:
        random.shuffle(matchList)
        
    for i, matchTuple in enumerate(matchList):
        if numMatches is not None and i > numMatches:
            break
        word, pronList = matchTuple
        print("%s: %s" % (word, ",".join(pronList)))
    print("")
    
    return matchList

# 2-syllable words with a stressed syllable containing 'dV' but not word initially
printOutMatches("dV", stressedSyllable="only", spanSyllable="no",
                wordInitial="no", numSyllables=2, numMatches=10)
 
# 3-syllable word with an 'ld' sequence that spans a syllable boundary
printOutMatches("lBd", wordInitial="no", multiword='no',
                numSyllables=3, numMatches=10)
 
# words ending in 'inth'
matchList = printOutMatches(u"ɪnɵ", wordFinal="only", numMatches=10)
 
# that also start with 's'
matchList = printOutMatches("s", wordInitial="only", numMatches=10,
                            matchList=matchList, multiword="no")
