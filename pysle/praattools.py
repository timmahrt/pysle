#encoding: utf-8
'''
Created on Oct 22, 2014

@author: tmahrt
'''


class OptionalFeatureError(ImportError):
    
    def __str__(self):
        return "ERROR: You must have praatio installed to use pysle.praatTools"

try:
    from praatio import tgio
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
    minT = tg.minTimestamp
    maxT = tg.maxTimestamp
    
    wordTier = tg.tierDict[wordTierName]
    phoneTier = tg.tierDict[phoneTierName]
    
    if skipLabelList is None:
        skipLabelList = []
    
    syllableEntryList = []
    tonicSEntryList = []
    tonicPEntryList = []
    
    for start, stop, word in wordTier.entryList:
        
        if word in skipLabelList:
            continue
        
        subPhoneTier = phoneTier.crop(start, stop, True, False)[0]
        
        # entry = (start, stop, phone)
        phoneList = [entry[2] for entry in subPhoneTier.entryList
                     if entry[2] != '']
        phoneList = [phoneList, ]
        
        try:
            sylTmp = pronunciationtools.findBestSyllabification(isleDict,
                                                                word,
                                                                phoneList)
        except isletool.WordNotInISLE:
            print("Word ('%s') not is isle -- skipping syllabification" % word)
            continue
        except (pronunciationtools.NullPronunciationError):
            print("Word ('%s') has no provided pronunciation" % word)
            continue
        
        for syllabificationResultList in sylTmp:
            stressI = syllabificationResultList[0]
            stressJ = syllabificationResultList[1]
            syllableList = syllabificationResultList[2]
                
            stressedPhone = None
            if stressI is not None and stressJ is not None:
                stressedPhone = syllableList[stressI][stressJ]
                syllableList[stressI][stressJ] += u"ˈ"
    
            i = 0
    #         print(syllableList)
            for k, syllable in enumerate(syllableList):
                
                # Create the syllable tier entry
                j = len(syllable)
                stubEntryList = subPhoneTier.entryList[i:i + j]
                i += j
                
                # The whole syllable was deleted
                if len(stubEntryList) == 0:
                    continue
                
                syllableStart = stubEntryList[0][0]
                syllableEnd = stubEntryList[-1][1]
                label = "-".join([entry[2] for entry in stubEntryList])
            
                syllableEntryList.append((syllableStart, syllableEnd, label))
                
                # Create the tonic syllable tier entry
                if k == stressI:
                    tonicSEntryList.append((syllableStart, syllableEnd, 'T'))
                
                # Create the tonic phone tier entry
                if k == stressI:
                    syllablePhoneTier = phoneTier.crop(syllableStart,
                                                       syllableEnd,
                                                       True, False)[0]
                
                    phoneList = [entry for entry in syllablePhoneTier.entryList
                                 if entry[2] != '']
                    justPhones = [phone for _, _, phone in phoneList]
                    cvList = pronunciationtools._prepPronunciation(justPhones)
                    
                    try:
                        tmpStressJ = cvList.index('V')
                    except ValueError:
                        for char in [u'r', u'n', u'l']:
                            if char in cvList:
                                tmpStressJ = cvList.index(char)
                                break
                            
                    phoneStart, phoneEnd = phoneList[tmpStressJ][:2]
                    tonicPEntryList.append((phoneStart, phoneEnd, 'T'))
    
    # Create a textgrid with the two syllable-level tiers
    syllableTier = tgio.IntervalTier('syllable', syllableEntryList,
                                     minT, maxT)
    tonicSTier = tgio.IntervalTier('tonicSyllable', tonicSEntryList,
                                   minT, maxT)
    tonicPTier = tgio.IntervalTier('tonicVowel', tonicPEntryList,
                                   minT, maxT)
    
    syllableTG = tgio.Textgrid()
    syllableTG.addTier(syllableTier)
    syllableTG.addTier(tonicSTier)
    syllableTG.addTier(tonicPTier)

    return syllableTG
