'''
Created on Oct 22, 2014

@author: tmahrt

An example of how to syllabify a textgrid.

This code is an optional feature of pysle that requires the
praatio library.
'''

from os.path import join

from praatio import tgio
from pysle import isletool
from pysle import praattools

root = join('.', 'files')
isleDict = isletool.LexicalTool(join(root, "ISLEdict_sample.txt"))

tg = tgio.openTextGrid(join(root, "pumpkins.TextGrid"))

# Get the syllabification tiers and add it to the textgrid
syllableTG = praattools.syllabifyTextgrid(isleDict, tg, "word", "phone",
                                          skipLabelList=["", ])
tg.addTier(syllableTG.tierDict["syllable"])
tg.addTier(syllableTG.tierDict["tonicSyllable"])
tg.addTier(syllableTG.tierDict["tonicVowel"])

tg.save(join(root, "pumpkins_with_syllables.TextGrid"))
