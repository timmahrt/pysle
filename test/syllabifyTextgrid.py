'''
Created on Oct 22, 2014

@author: tmahrt

This example was originally meant to show how you can use the library
to modify a textgrid.  It still shows that, but all that code is now in
the main library (pysle.praattools.syllabifyTextgrid)

This snippet shows you how to use this function.
'''

from os.path import join

from praatio import tgio
from pysle import isletool
from pysle import praattools

path = join('.', 'files')
path = "/Users/tmahrt/Dropbox/workspace/pysle/test/files"

tg = tgio.openTextGrid(join(path, "pumpkins.TextGrid"))

# Needs the full path to the file
islevPath = '/Users/tmahrt/Dropbox/workspace/pysle/test/islev2.txt'
isleDict = isletool.LexicalTool(islevPath)

# Get the syllabification tiers and add it to the textgrid
syllableTG = praattools.syllabifyTextgrid(isleDict, tg, "word", "phone",
                                          skipLabelList=["",])
tg.addTier(syllableTG.tierDict["syllable"])
tg.addTier(syllableTG.tierDict["tonic"])



tg.save(join(path, "pumpkins_with_syllables.TextGrid"))


        
