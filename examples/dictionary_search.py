# encoding: utf-8
"""
Examples of how to use pysle's regular-expression-based
search functionality.
"""

from pysle import isletool

isle = isletool.Isle()


def printOutMatches(
    matchStr,
    numSyllables=None,
    wordInitial="ok",
    wordFinal="ok",
    spanSyllable="ok",
    stressedSyllable="ok",
    multiword="ok",
    numMatches=None,
    pos=None,
    exactMatch=False,
    randomize=True,
):
    """Helper function to run searches and output results"""
    for i, wordInfo in enumerate(
        isle.search(
            matchStr,
            numSyllables,
            wordInitial,
            wordFinal,
            spanSyllable,
            stressedSyllable,
            multiword,
            pos,
            exactMatch,
            randomize,
        )
    ):
        word = wordInfo["word"]
        pronunciation = wordInfo["pronunciation"]

        print(f"{word}: {pronunciation}")

        if numMatches and i >= numMatches:
            break
    print("---------")


# 2-syllable words with a stressed syllable containing 'dV'
# but not word initially
printOutMatches(
    "dV",
    stressedSyllable="only",
    spanSyllable="no",
    wordInitial="no",
    numSyllables=2,
    numMatches=5,
)

# 3-syllable word with an 'ld' sequence that spans a syllable boundary
printOutMatches(
    "lBd", wordInitial="no", multiword="no", numSyllables=3, numMatches=5, pos="nn"
)

# words ending in 'inth'
printOutMatches("ɪnɵ", wordFinal="only", numMatches=5)

# that also start with 's'
printOutMatches("s", wordInitial="only", numMatches=5, multiword="no")

# words pronounced exactly as "kæt"
printOutMatches("kæt", exactMatch=True)

# all words containing "kæt"
printOutMatches("kæt", numMatches=5)
