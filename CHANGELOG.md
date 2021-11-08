
# Pysle Changelog

*Pysle uses semantic versioning (Major.Minor.Patch)*

Ver 3.1 (Nov 8, 2021)
- added a fallback method to findBestSyllabification for out-of-dictionary words ending in "'s"

Ver 3.0 (Oct 30, 2021)
- dropping support for python 2.7
- some important bugfixes related to syllabification estimation

Ver 2.3 (Nov 18, 2020)
- add exactMatch to isletool.search()
    - when True, will return exact phonetic matches, ignoring stress, syllable, and word markers
    - see examples/dictionary_search.py

Ver 2.2 (Nov 17, 2020)
- the ISLEdict is now bundled with pysle--no need to download it separately!
- loading the isleDict is ~10% faster

Ver 2.1 (May 31, 2020)
- add transcribe function, given a word or series of words, get a possible pronunciation;
    - see examples/isletool_examples.py

Ver 2.0 (May 27, 2020)
- cleaned up the api a little, including some functions that weren't usable
- updated documentation and readme files.  Added pdoc documentation

Ver 1.5 (March 3, 2017)
- substantial bugfixes made, particularly to the syllable-marking code

Ver 1.4 (July 9, 2016)
- added search functionality
- ported code to use the new unicode IPA-based isledict
    - (the old one was ascii)
- (Oct 20, 2016) Integration tests added; using Travis CI and Coveralls
    - for build automation.  No new functionality added.

Ver 1.3 (March 15, 2016)
- added indicies for stressed vowels

Ver 1.2 (June 20, 2015)
- Python 3.x support

Ver 1.1 (January 30, 2015)
- word lookup ~65 times faster

Ver 1.0 (October 23, 2014)
- first public release.
