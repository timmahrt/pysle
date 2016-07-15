#encoding: utf-8
'''
Created on Oct 15, 2014

@author: tmahrt
'''

import itertools

from pysle import isletool


class NullPronunciationError(Exception):
    
    def __init__(self, word):
        super(NullPronunciationError, self).__init__()
        self.word = word
    
    def __str__(self):
        return "No pronunciation given for word '%s'" % self.word


class NullPhoneError(Exception):

    def __str(self):
        return "Received an empty phone in the pronunciation list"
    

def _lcs_lens(xs, ys):
    curr = list(itertools.repeat(0, 1 + len(ys)))
    for x in xs:
        prev = list(curr)
        for i, y in enumerate(ys):
            if x == y:
                curr[i + 1] = prev[i] + 1
            else:
                curr[i + 1] = max(curr[i], prev[i + 1])
    return curr


def _lcs(xs, ys):
    nx, ny = len(xs), len(ys)
    if nx == 0:
        return []
    elif nx == 1:
        return [xs[0]] if xs[0] in ys else []
    else:
        i = nx // 2
        xb, xe = xs[:i], xs[i:]
        ll_b = _lcs_lens(xb, ys)
        ll_e = _lcs_lens(xe[::-1], ys[::-1])
        _, k = max((ll_b[j] + ll_e[ny - j], j)
                   for j in range(ny + 1))
        yb, ye = ys[:k], ys[k:]
        return _lcs(xb, yb) + _lcs(xe, ye)


def _prepPronunciation(phoneList):
    retList = []
    for phone in phoneList:
        if 'r' in phone:
            phone = ['r', ]
        try:
            phone = phone[0]  # Only represent the string by its first letter
            phone = phone.lower()
        except IndexError:
            raise NullPhoneError()
        
        if phone in isletool.vowelList:
            phone = 'V'
        retList.append(phone)
    
    return retList


def _adjustSyllabification(adjustedPhoneList, syllableList):
    '''
    Inserts spaces into a syllable if needed
    
    Originally the phone list and syllable list contained the same number
    of phones.  But the adjustedPhoneList may have some insertions which are
    not accounted for in the syllableList.
    '''
    i = 0
    retSyllableList = []
    for syllable in syllableList:
        j = len(syllable)
        tmpPhoneList = adjustedPhoneList[i:i + j]
        numBlanks = -1
        phoneList = tmpPhoneList[:]
        while numBlanks != 0:
            
            numBlanks = tmpPhoneList.count("''")
            if numBlanks > 0:
                tmpPhoneList = adjustedPhoneList[i + j:i + j + numBlanks]
                phoneList.extend(tmpPhoneList)
                j += numBlanks
        
        for k, phone in enumerate(phoneList):
            if phone == "''":
                syllable.insert(k, "''")
        
        i += j
        
        retSyllableList.append(syllable)
    
    return retSyllableList
        

def _findBestPronunciation(isleDict, wordText, aPron):
    '''
    Words may have multiple candidates in ISLE; returns the 'optimal' one.
    '''
    if len(aPron) == 0:
        raise NullPronunciationError(wordText)
    
    isleWordList = isleDict.lookup(wordText)
    
    aP = _prepPronunciation(aPron)  # Mapping to simplified phone inventory
    
    origPronDict = dict((newPron, oldPron)
                        for newPron, oldPron in zip(aP, aPron))
    
    numDiffList = []
    withStress = []
    i = 0
    alignedSyllabificationList = []
    alignedActualPronunciationList = []
    for wordTuple in isleWordList:
        syllableList = wordTuple[0]  # syllableList, stressList
        
        iP = [phone for phoneList in syllableList for phone in phoneList]
        iP = _prepPronunciation(iP)

        alignedIP, alignedAP = alignPronunciations(iP, aP)
        
        # Remapping to actual phones
        alignedAP = [origPronDict.get(phon, "''") for phon in alignedAP]
        alignedActualPronunciationList.append(alignedAP)
        
        # Adjusting the syllabification for differences between the dictionary
        # pronunciation and the actual pronunciation
        alignedSyllabification = _adjustSyllabification(alignedIP,
                                                        syllableList)
        alignedSyllabificationList.append(alignedSyllabification)
        
        # Count the number of misalignments between the two
        numDiff = alignedIP.count("''") + alignedAP.count("''")
        numDiffList.append(numDiff)
        
        # Is there stress in this word
        hasStress = False
        for syllable in syllableList:
            for phone in syllable:
                hasStress = u"ˈ" in phone or hasStress
        
        if hasStress:
            withStress.append(i)
        i += 1
    
    # Return the pronunciation that had the fewest differences
    #     to the actual pronunciation
    minDiff = min(numDiffList)
    
    # When there are multiple candidates that have the minimum number
    #     of differences, prefer one that has stress in it
    bestIndex = None
    bestIsStressed = None
    for i, numDiff in enumerate(numDiffList):
        if numDiff != minDiff:
            continue
        if bestIndex is None:
            bestIndex = i
            bestIsStressed = i in withStress
        else:
            if not bestIsStressed and i in withStress:
                bestIndex = i
                bestIsStressed = True
    
    return (isleWordList, alignedActualPronunciationList,
            alignedSyllabificationList, bestIndex)


def _syllabifyPhones(phoneList, syllableList, isleStressList):
    '''
    Given a phone list and a syllable list, syllabify the phones
    
    Typically used by findBestSyllabification which first aligns the phoneList
    with a dictionary phoneList and then uses the dictionary syllabification
    to syllabify the input phoneList.
    '''
    try:
        stressIndex = isleStressList[0]
    except IndexError:
        stressIndex = None
    
    numPhoneList = [len(syllable) for syllable in syllableList]
    
    start = 0
    syllabifiedList = []
    for end in numPhoneList:
        
        syllable = phoneList[start:start + end]
        syllabifiedList.append(syllable)
        
        start += end
    
    return stressIndex, syllabifiedList


def alignPronunciations(pronI, pronA):
    '''
    Align the phones in two pronunciations
    '''
    
    # First prep the two pronunctions
    pronI = [char for char in pronI]
    pronA = [char for char in pronA]
    
    # Remove any elements not in the other list (but maintain order)
    pronITmp = pronI
    pronATmp = pronA

    # Find the longest sequence
    sequence = _lcs(pronITmp, pronATmp)

    # Find the index of the sequence
    # TODO: investigate ambiguous cases
    startA = 0
    startI = 0
    sequenceIndexListA = []
    sequenceIndexListI = []
    for phone in sequence:
        startA = pronA.index(phone, startA)
        startI = pronI.index(phone, startI)
        
        sequenceIndexListA.append(startA)
        sequenceIndexListI.append(startI)
    
    # An index on the tail of both will be used to create output strings
    # of the same length
    sequenceIndexListA.append(len(pronA))
    sequenceIndexListI.append(len(pronI))
    
    # Fill in any blanks such that the sequential items have the same
    # index and the two strings are the same length
    for x in range(len(sequenceIndexListA)):
        indexA = sequenceIndexListA[x]
        indexI = sequenceIndexListI[x]
        if indexA < indexI:
            for x in range(indexI - indexA):
                pronA.insert(indexA, "''")
            sequenceIndexListA = [val + indexI - indexA
                                  for val in sequenceIndexListA]
        elif indexA > indexI:
            for x in range(indexA - indexI):
                pronI.insert(indexI, "''")
            sequenceIndexListI = [val + indexA - indexI
                                  for val in sequenceIndexListI]
    
    return pronI, pronA
   

def findBestSyllabification(isleDict, wordText, actualPronunciationList):
    '''
    Find the best syllabification for a word
    
    First find the closest pronunciation to a given pronunciation. Then take
    the syllabification for that pronunciation and map it onto the
    input pronunciation.
    '''
    retList = _findBestPronunciation(isleDict, wordText,
                                     actualPronunciationList)
    isleWordList, alignedAPronList, alignedSyllableList, bestIndex = retList
    
    alignedPhoneList = alignedAPronList[bestIndex]
    alignedSyllables = alignedSyllableList[bestIndex]
    syllabification = isleWordList[bestIndex][0]
    stressedSyllableIndexList = isleWordList[bestIndex][1]
    stressedPhoneIndexList = isleWordList[bestIndex][2]
    
    stressedSyllable, syllableList = _syllabifyPhones(alignedPhoneList,
                                                      alignedSyllables,
                                                      stressedSyllableIndexList)
    
    # Count the index of the stressed phones, if the stress list has
    # become flattened (no syllable information)
    flattenedStressIndexList = []
    for i, j in zip(stressedSyllableIndexList, stressedPhoneIndexList):
        k = j
        for l in range(i):
            k += len(syllableList[l])
        flattenedStressIndexList.append(k)
    
    return (stressedSyllable, syllableList, syllabification,
            stressedSyllableIndexList, stressedPhoneIndexList,
            flattenedStressIndexList)


def findClosestPronunciation(isleDict, wordText, aPron):
    '''
    Find the closest dictionary pronunciation to a provided pronunciation
    '''
    
    retList = _findBestPronunciation(isleDict, wordText, aPron)
    isleWordList = retList[0]
    bestIndex = retList[3]
    
    return isleWordList[bestIndex]
