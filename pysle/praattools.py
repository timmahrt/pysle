'''
Created on Oct 22, 2014

@author: tmahrt
'''

class OptionalFeatureError(ImportError):
    
    def __str__(self):
        return "ERROR: You must have praatio installed to use pysle.praatTools"

try:
    import praatio
except ImportError:
    raise OptionalFeatureError()

from pysle import isletool
from pysle import pronunciationtools


def syllabifyTextgrid(isleDict, tg, wordTierName, phoneTierName, 
                      skipLabelList=None):
    '''
    Given a textgrid, syllabifies the phones in the textgrid
    
    skipLabelList allows you to skip labels without generating warnings
    (e.g. '', 'sp', etc.)
    
    The textgrid must have a word tier and a phone tier.
    
    Returns a textgrid with only two tiers containing syllable information
    (syllabification of the phone tier and a tier marking word-stress).
    '''
    wordTier = tg.tierDict[wordTierName]
    phoneTier = tg.tierDict[phoneTierName]
    
    if skipLabelList == None:
        skipLabelList = []
    
    syllableEntryList = []
    tonicEntryList = []
    for start, stop, word in wordTier.entryList:
        
        if word in skipLabelList:
            continue
        
        subPhoneTier = phoneTier.crop(start, stop, True, False)[0]
        
        phoneList = [phone for startP, endP, phone in subPhoneTier.entryList if phone != '']
        
        try:
            returnList = pronunciationtools.findBestSyllabification(isleDict, 
                                                                    word, 
                                                                    phoneList)
        except isletool.WordNotInISLE:
            print "Word ('%s') not is isle -- skipping syllabification" % word
            continue
        except (pronunciationtools.NullPronunciationError):
            print "Word ('%s') has no provided pronunciation" % word
            continue
    
        stressedSyllable, syllableList, syllabification, stressIndexList = returnList
        
        i = 0
#         print syllableList
        for k, syllable in enumerate(syllableList):
            
            # Create the syllable tier entry
            j = len(syllable)
            stubEntryList = subPhoneTier.entryList[i:i+j]
            i += j
            
            # The whole syllable was deleted
            if len(stubEntryList) == 0:
                continue
            
            syllableStart = stubEntryList[0][0]
            syllableEnd = stubEntryList[-1][1]
            label = "-".join([phone for start, end, phone in stubEntryList])
        
            syllableEntryList.append( (syllableStart, syllableEnd, label) )
            
            # Create the tonic tier entry
            try:
                stressIndex = stressIndexList[0]
            except IndexError:
                stressIndex = None # Function word probably
                
            tonicLabel = ''
            if k == stressIndex:
                tonicLabel = 'T'
                
            tonicEntryList.append( (syllableStart, syllableEnd, tonicLabel) )
    
    # Create a textgrid with the two syllable-level tiers
    syllableTier = praatio.TextgridTier("syllable", syllableEntryList, praatio.INTERVAL_TIER)
    tonicTier = praatio.TextgridTier('tonic', tonicEntryList, praatio.INTERVAL_TIER)
    
    syllableTG = praatio.Textgrid()
    syllableTG.addTier(syllableTier)
    syllableTG.addTier(tonicTier)

    return syllableTG

