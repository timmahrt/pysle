
---------
pysle
---------

.. image:: https://travis-ci.org/timmahrt/pysle.svg?branch=master
    :target: https://travis-ci.org/timmahrt/pysle

.. image:: https://coveralls.io/repos/github/timmahrt/pysle/badge.svg?branch=master
    :target: https://coveralls.io/github/timmahrt/pysle?branch=master

.. image:: https://img.shields.io/badge/license-MIT-blue.svg?
   :target: http://opensource.org/licenses/MIT
   
*Questions?  Comments?  Feedback?  Chat with us on gitter!*

.. image:: https://badges.gitter.im/pysle/Lobby.svg?
   :alt: Join the chat at https://gitter.im/pysle/Lobby
   :target: https://gitter.im/pysle/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

-----

Pronounced like 'p' + 'isle'.

An interface to a pronunciation dictionary with stress markings
(ISLEX - the international speech lexicon), 
along with some tools for working with comparing and aligning 
pronunciations (e.g. a list of phones someone said versus a standard or 
canonical dictionary pronunciation). 


.. sectnum::
.. contents::


Common Use Cases
================

What can you do with this library?

- look up the list of phones and syllables for canonical pronunciations 
  of a word::
  
    pysle.isletool.LexicalTool.lookup('cat')

- map an actual pronunciation to a dictionary pronunciation (can be used 
  to automatically find speech errors)::
  
    pysle.pronunciationtools.findClosestPronunciation(isleDict, 'cat', ['k', 'æ',])

- automatically syllabify a praat textgrid containing words and phones 
  (e.g. force-aligned text) -- requires my 
  `praatIO <https://github.com/timmahrt/praatIO>`_ library::
  
    pysle.syllabifyTextgrid(isleDict, praatioTextgrid, "words", "phones")

- search for words based on pronunciation::

    e.g. Words that start with a sound, or have a sound word medially, or 
    in stressed vowel position, etc.
    
    see /tests/dictionary_search.py
    
Major revisions
================

Ver 1.5 (March 3, 2017)

- substantial bugfixes made, particularly to the syllable-marking code

Ver 1.4 (July 9, 2016)

- added search functionality

- ported code to use the new unicode IPA-based isledict
  (the old one was ascii)

- (Oct 20, 2016) Integration tests added; using Travis CI and Coveralls
  for build automation.  No new functionality added.

Ver 1.3 (March 15, 2016)

- added indicies for stressed vowels

Ver 1.2 (June 20, 2015)

- Python 3.x support

Ver 1.1 (January 30, 2015)

- word lookup ~65 times faster

Ver 1.0 (October 23, 2014)

- first public release.


Requirements
================

- Before you use this library (before or after installing it) you will need
  to download the ILSEX dictionary.  It can be downloaded here under the
  section 'English' linked under the text 'English Pronlex'
  (with a file name of ISLEdict.txt):

  `ISLEX project page <http://isle.illinois.edu/sst/data/g2ps/>`_

  `Direct link to the ISLEX file used in this project
  <http://isle.illinois.edu/sst/data/g2ps/English/ISLEdict.txt>`_ (ISLEdict.txt)

- ``Python 2.7.*`` or above

- ``Python 3.3.*`` or above (or below, probably)

- The `praatIO <https://github.com/timmahrt/praatIO>`_ library is required IF 
  you want to use the textgrid functionality.  It is not required 
  for normal use.


Installation
================

If you on Windows, you can use the installer found here (check that it is up to date though)
`Windows installer <http://www.timmahrt.com/python_installers>`_

Psyle is on pypi and can be installed or upgraded from the command-line shell with pip like so::

    python -m pip install psyle --upgrade

Otherwise, to manually install, after downloading the source from github, from a command-line shell, navigate to the directory containing setup.py and type::

    python setup.py install

If python is not in your path, you'll need to enter the full path e.g.::

	C:\Python36\python.exe setup.py install

	
Example usage
================

Here is a typical common usage::

    from pysle import isle
    isleDict = isle.LexicalTool('C:\islev2.dict')
    print isleDict.lookup('catatonic')[0] # Get the first pronunciation
    >> [['k', 'ˌæ'], ['t˺', 'ə'], ['t', 'ˈɑ'], ['n', 'ɪ', 'k']] [2, 0]

and another::

    from pysle import isle
    from psyle import pronunciationTools
    
    searchWord = 'another'
    anotherPhoneList = ['n', '@', 'th', 'r'] # Actually produced (ASCII or IPA ok here)

    returnList = pronunciationTools.findBestSyllabification(isleDict, 
                                                            searchWord, 
                                                            anotherPhoneList)
    print syllableList
    >> [["''"], ['n', '@'], ['th', 'r']]
    

Please see \\examples for example usage


Citing pysle
===============

Pysle is general purpose coding and doesn't need to be cited
(you should cite the
`ISLEX project <http://isle.illinois.edu/sst/data/g2ps/>`_
instead) but if you would like to, it can be cited like so:

Tim Mahrt. Pysle. https://github.com/timmahrt/pysle, 2016.


Acknowledgements
================

Development of Pysle was possible thanks to NSF grant **IIS 07-03624**
to Jennifer Cole and Mark Hasegawa-Johnson, NSF grant **BCS 12-51343**
to Jennifer Cole, José Hualde, and Caroline Smith, and
to the A*MIDEX project (n° **ANR-11-IDEX-0001-02**) to James Sneed German
funded by the Investissements d'Avenir French Government program, managed
by the French National Research Agency (ANR).
