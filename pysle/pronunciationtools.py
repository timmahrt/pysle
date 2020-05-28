#encoding: utf-8
'''
Code for comparing and aligning pronunciation data with pronunciations found in the ISLE dictionary.

see **examples/pronunciationtools_examples.py**
'''

import itertools
import copy

from pysle import isletool


class TooManyVowelsInSyllable(Exception):

    def __init__(self, syllable, syllableCVMapped):
        super(TooManyVowelsInSyllable, self).__init__()
        self.syllable = syllable
        self.syllableCVMapped = syllableCVMapped

    def __str__(self):
        errStr = ("Error: syllable '%s' found to have more than "
                  "one vowel.\n This was the CV mapping: '%s'")
        syllableStr = u"".join(self.syllable)
        syllableCVStr = u"".join(self.syllableCVMapped)

        return errStr % (syllableStr, syllableCVStr)


class NumWordsMismatchError(Exception):

    def __init__(self, word, numMatches):
        super(NumWordsMismatchError, self).__init__()
        self.word = word
        self.numMatches = numMatches

    def __str__(self):
        errStr = ("Error: %d matches found in isleDict for '%s'.\n"
                  "Only 1 match allowed--likely you need to break"
                  "up your query text into separate words.")
        return errStr % (self.numMatches, self.word)


class WrongTypeError(Exception):

    def __init__(self, errMsg):
        super(WrongTypeError, self).__init__()
        self.str = errMsg

    def __str__(self):
        return self.str


class NullPronunciationError(Exception):

    def __init__(self, word):
        super(NullPronunciationError, self).__init__()
        self.word = word

    def __str__(self):
        return "No pronunciation given for word '%s'" % self.word


class NullPhoneError(Exception):

    def __str__(self):
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

    if nx == 1:
        return [xs[0]] if xs[0] in ys else []

    i = nx // 2
    xb, xe = xs[:i], xs[i:]
    ll_b = _lcs_lens(xb, ys)
    ll_e = _lcs_lens(xe[::-1], ys[::-1])
    _, k = max((ll_b[j] + ll_e[ny - j], j)
               for j in range(ny + 1))
    yb, ye = ys[:k], ys[k:]
    return _lcs(xb, yb) + _lcs(xe, ye)


def simplifyPronunciation(phoneList):
    '''
    Simplifies pronunciation

    Removes diacritics and unifies vowels and rhotics
    '''
    retList = []
    for phone in phoneList:

        # Remove diacritics
        for diacritic in isletool.diacriticList:
            phone = phone.replace(diacritic, u'')

        # Unify rhotics
        if 'r' in phone:
            phone = 'r'

        phone = phone.lower()

        # Unify vowels
        if isletool.isVowel(phone):
            phone = u'V'

        # Only represent the string by its first letter
        try:
            phone = phone[0]
        except IndexError:
            raise NullPhoneError()

        # Unify vowels (reducing the vowel to one char)
        if isletool.isVowel(phone):
            phone = u'V'

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
    for syllableNum, syllable in enumerate(syllableList):
        j = len(syllable)
        if syllableNum == len(syllableList) - 1:
            j = len(adjustedPhoneList) - i
        tmpPhoneList = adjustedPhoneList[i:i + j]
        numBlanks = -1
        phoneList = tmpPhoneList[:]
        while numBlanks != 0:

            numBlanks = tmpPhoneList.count(u"''")
            if numBlanks > 0:
                tmpPhoneList = adjustedPhoneList[i + j:i + j + numBlanks]
                phoneList.extend(tmpPhoneList)
                j += numBlanks

        for k, phone in enumerate(phoneList):
            if phone == u"''":
                syllable.insert(k, u"''")

        i += j

        retSyllableList.append(syllable)

    return retSyllableList


def _findBestPronunciation(isleWordList, aPron):
    '''
    Words may have multiple candidates in ISLE; returns the 'optimal' one.
    '''

    aP = simplifyPronunciation(aPron)  # Mapping to simplified phone inventory

    numDiffList = []
    withStress = []
    i = 0
    alignedSyllabificationList = []
    alignedActualPronunciationList = []
    for wordTuple in isleWordList:
        aPronMap = copy.deepcopy(aPron)
        syllableList = wordTuple[0]  # syllableList, stressList

        iP = [phone for phoneList in syllableList for phone in phoneList]
        iP = simplifyPronunciation(iP)

        alignedIP, alignedAP = alignPronunciations(iP, aP)

        # Remapping to actual phones
#         alignedAP = [origPronDict.get(phon, u"''") for phon in alignedAP]
        alignedAP = [aPronMap.pop(0) if phon != u"''" else u"''"
                     for phon in alignedAP]
        alignedActualPronunciationList.append(alignedAP)

        # Adjusting the syllabification for differences between the dictionary
        # pronunciation and the actual pronunciation
        alignedSyllabification = _adjustSyllabification(alignedIP,
                                                        syllableList)
        alignedSyllabificationList.append(alignedSyllabification)

        # Count the number of misalignments between the two
        numDiff = alignedIP.count(u"''") + alignedAP.count(u"''")
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


def _syllabifyPhones(phoneList, syllableList):
    '''
    Given a phone list and a syllable list, syllabify the phones

    Typically used by findBestSyllabification which first aligns the phoneList
    with a dictionary phoneList and then uses the dictionary syllabification
    to syllabify the input phoneList.
    '''

    numPhoneList = [len(syllable) for syllable in syllableList]

    start = 0
    syllabifiedList = []
    for end in numPhoneList:

        syllable = phoneList[start:start + end]
        syllabifiedList.append(syllable)

        start += end

    return syllabifiedList


def alignPronunciations(phoneListA, phoneListB):
    '''
    Align the phones in two pronunciations

    This will find the longest (non-continuous) common sequence and fill in the gaps
    before, between, and after the characters such that the common elements
    occur at the same points and the character strings are the same length

    In the following example, the phone lists share the sequence ['a', 'd']

    ```python
    phoneListA = ['a', 'b', 'c', 'd', 'e', 'f']
    phoneListB = ['l', 'a', 'z', 'd', 'u']
    a, b = alignPronunciations(phoneListA, phoneListB)
    print(a) > ["''", 'a', 'b', 'c', 'd', 'e', 'f']
    print(b) > ['l', 'a', 'z', "''", 'd', 'u', "''"]
    ```
    '''

    # Remove any elements not in the other list (but maintain order)
    pronATmp = phoneListA
    pronBTmp = phoneListB

    # Find the longest sequence
    sequence = _lcs(pronBTmp, pronATmp)

    # Find the index of the sequence
    # TODO: investigate ambiguous cases
    startA = 0
    startB = 0
    sequenceIndexListA = []
    sequenceIndexListB = []
    for phone in sequence:
        startA = phoneListA.index(phone, startA)
        startB = phoneListB.index(phone, startB)

        sequenceIndexListA.append(startA)
        sequenceIndexListB.append(startB)

    # An index on the tail of both will be used to create output strings
    # of the same length
    sequenceIndexListA.append(len(phoneListA))
    sequenceIndexListB.append(len(phoneListB))

    # Fill in any blanks such that the sequential items have the same
    # index and the two strings are the same length
    for i, _ in enumerate(sequenceIndexListA):
        indexA = sequenceIndexListA[i]
        indexB = sequenceIndexListB[i]
        if indexA < indexB:
            for _ in range(indexB - indexA):
                phoneListA.insert(indexA, "''")
            sequenceIndexListA = [val + indexB - indexA
                                  for val in sequenceIndexListA]
        elif indexA > indexB:
            for _ in range(indexA - indexB):
                phoneListB.insert(indexB, "''")
            sequenceIndexListB = [val + indexA - indexB
                                  for val in sequenceIndexListB]

    return phoneListA, phoneListB


def findBestSyllabification(isleDict, wordText, phoneList):
    '''
    Find the best syllabification for a word

    First find the closest pronunciation to a given pronunciation. Then take
    the syllabification for that pronunciation and map it onto the
    input pronunciation.
    '''
    try:
        phoneList = [unicode(char, "utf-8") for phone in phoneList]
    except (NameError, TypeError):
        pass

    isleWordList = isleDict.lookup(wordText)[0]

    return _findBestSyllabification(isleWordList, phoneList)


def _findBestSyllabification(inputIsleWordList, actualPronunciationList):
    '''
    Find the best syllabification for a word

    First find the closest pronunciation to a given pronunciation. Then take
    the syllabification for that pronunciation and map it onto the
    input pronunciation.
    '''
    retList = _findBestPronunciation(inputIsleWordList,
                                     actualPronunciationList)
    isleWordList, alignedAPronList, alignedSyllableList, bestIndex = retList

    alignedPhoneList = alignedAPronList[bestIndex]
    alignedSyllables = alignedSyllableList[bestIndex]
    syllabification = isleWordList[bestIndex][0]
    stressedSyllableIndexList = isleWordList[bestIndex][1]
    stressedPhoneIndexList = isleWordList[bestIndex][2]

    syllableList = _syllabifyPhones(alignedPhoneList, alignedSyllables)

    # Get the location of stress in the generated file
    try:
        stressedSyllableI = stressedSyllableIndexList[0]
    except IndexError:
        stressedSyllableI = None
        stressedVowelI = None
    else:
        stressedVowelI = _getSyllableNucleus(syllableList[stressedSyllableI])

    # Count the index of the stressed phones, if the stress list has
    # become flattened (no syllable information)
    flattenedStressIndexList = []
    for i, j in zip(stressedSyllableIndexList, stressedPhoneIndexList):
        k = j
        for l in range(i):
            k += len(syllableList[l])
        flattenedStressIndexList.append(k)

    return (stressedSyllableI, stressedVowelI, syllableList, syllabification,
            stressedSyllableIndexList, stressedPhoneIndexList,
            flattenedStressIndexList)


def _getSyllableNucleus(phoneList):
    '''
    Given the phones in a syllable, retrieves the vowel index
    '''
    cvList = ['V' if isletool.isVowel(phone) else 'C' for phone in phoneList]

    vowelCount = cvList.count('V')
    if vowelCount > 1:
        raise TooManyVowelsInSyllable(phoneList, cvList)

    if vowelCount == 1:
        stressI = cvList.index('V')
    else:
        stressI = None

    return stressI


def findClosestPronunciation(isleDict, word, phoneList):
    '''
    Find the closest dictionary pronunciation to a provided pronunciation
    '''
    isleWordList = isleDict.lookup(word)

    retList = _findBestPronunciation(isleWordList[0], phoneList)
    isleWordList = retList[0]
    bestIndex = retList[3]

    return isleWordList[bestIndex]
