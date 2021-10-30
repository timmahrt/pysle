#encoding: utf-8
'''
An example of how to syllabify a textgrid.

This code is an optional feature of pysle that requires the
praatio library.
'''

from os.path import join

from praatio import textgrid
from pysle import isletool
from pysle import praattools

root = join('.', 'files')
isleDict = isletool.LexicalTool(join(root, "ISLEdict_sample.txt"))

tg = textgrid.openTextgrid(join(root, "problematicdx.TextGrid"), includeEmptyIntervals=False)

# Get the syllabification tiers and add it to the textgrid
syllableTG = praattools.syllabifyTextgrid(isleDict, tg, "word", "phone",
                                          skipLabelList=["", ], stressedSyllableDetectionErrors="WARN", syllabificationError="WARN")
tg.addTier(syllableTG.tierDict["syllable"])
tg.addTier(syllableTG.tierDict["tonicSyllable"])
tg.addTier(syllableTG.tierDict["tonicVowel"])

tg.save(join(root, "problematicdx_with_syllables.TextGrid"), format="short_textgrid", includeBlankSpaces=True)
