
---------
pysle
---------

.. sectnum::
.. contents::

Pronounced like 'p' + 'isle'.

An interface for the ILSEX (international speech lexicon) dictionary, 
along with some tools for working with comparing and aligning 
pronunciations (e.g. a list of phones someone said versus a standard or 
canonical dictionary pronunciation). 


Common Use Cases
================

What can you do with this library?

- look up the list of phones and syllables for canonical pronunciations 
  of a word::
  
    pysle.isletool.LexicalTool.lookup('cat')

- map an actual pronunciation to a dictionary pronunciation (can be used 
  to automatically find speech errors)::
  
    pysle.pronunciationtools.findClosestPronunciation(isleDict, 'cat', ['kh', 'ae',]) 

- automatically syllabify a praat textgrid containing words and phones 
  (e.g. force-aligned text) -- requires my 
  `praatIO <https://github.com/timmahrt/praatIO>`_ library::
  
    pysle.syllabifyTextgrid(isleDict, praatioTextgrid, "words", "phones")


Requirements
================

- Before you use this library (before or after installing it) you will need
  to download the ILSEX dictionary.  It can be downloaded here:

  `ISLEX project page <http://www.isle.illinois.edu/sst/data/dict/>`_

  `Direct link to the ISLEX file used in this project
  <http://www.isle.illinois.edu/sst/data/dict/islev2.txt)>`_ (islev2.txt)

- ``Python 2.7.*`` or above

- The `praatIO <https://github.com/timmahrt/praatIO>`_ library is required IF 
  you want to use the textgrid functionality.  It is not required 
  for normal use.


Installation
================

From a command-line shell, navigate to the directory this is located in 
and type::

	python setup.py install

If python is not in your path, you'll need to enter the full path e.g.::

	C:\Python27\python.exe setup.py install

	
Example usage
================

Here is a typical common usage::

    from pysle import isle
    isleDict = isle.LexicalTool('C:\islev2.dict')
    print isleDict.lookup('catatonic')[0] # Get the first pronunciation
    >> [['kh', '@,'], ['t_(', '&'], ['th', "A'"], ['n', 'I', 'kh']] [2]

and another::

    from pysle import isle
    from psyle import pronunciationTools
    
    searchWord = 'another'
    anotherPhoneList = ['n', '@', 'th', 'r'] # Actually produced

    returnList = pronunciationTools.findBestSyllabification(isleDict, 
                                                            searchWord, 
                                                            anotherPhoneList)
    print syllableList
    >> [["''"], ['n', '@'], ['th', 'r']]
    

Please see \\test for example usage

