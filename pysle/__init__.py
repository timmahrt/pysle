#encoding: utf-8
"""
Pysle is an interface to the ISLEX English pronunciation dictionary

ISLEX contains multiple variations in pronunciations for words--
like [b ɚ ɹ d] or [b ˈɝ d] for 'bird'.  It contains primary and
secondary stress information as in [ˈɛ . l ə . v ˌei . ɾ ɚ] for 'elevator'

Using pysle, you can query this resource.

**isletool.py** contains the fundamental parts of the code.  This
code is responsible for looking up words and getting their
pronunciation. With the search() function, you can look up words
based on their pronunication too.  For example, every word that
starts with a vowel or that ends in
[k æ t] ('scat', 'cat', 'muscat'), etc.

**pronunciationtools.py** contains useful utilities when working
with a corpus of pronunciation data.  You can compare pronunciations
from your own data with "ideal" pronunciations from the ISLEX dictionary.
Such data can be used to explore speech data--which syllables are
expected to be stressed?  Are there phones or syllables that might
have been dropped in the pronunciation?

**praattools.py** contains useful utilities if you are working
specifically with data stored in TextGrids.  Praat is a speech
analysis tool that stores speech annotation data--such as phone
labels--in TextGrids.
"""
