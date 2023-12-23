
# pysle

[![](https://app.travis-ci.com/timmahrt/pysle.svg?branch=main)](https://app.travis-ci.com/github/timmahrt/pysle) [![](https://coveralls.io/repos/github/timmahrt/pysle/badge.svg?)](https://coveralls.io/github/timmahrt/pysle?branch=main) [![](https://img.shields.io/badge/license-MIT-blue.svg?)](http://opensource.org/licenses/MIT) [![](https://img.shields.io/pypi/v/pysle.svg)](https://pypi.org/project/pysle/)

*Questions?  Comments?  Feedback? [![](https://badges.gitter.im/pysle/Lobby.svg)](https://gitter.im/pysle/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)*

-----

Pronounced like 'p' + 'isle'.

An interface to a pronunciation dictionary with stress markings
(ISLEX - the international speech lexicon),
along with some tools for working with comparing and aligning
pronunciations (e.g. a list of phones someone said versus a standard or
canonical dictionary pronunciation).


# Table of contents
1. [Documentation](#documentation)
2. [Tutorials](#tutorials)
3. [Version History](#version-history)
4. [Requirements](#requirements)
5. [ISLE Dictionary](#isle-dictionary)
6. [Installation](#installation)
7. [Upgrading](#upgrading)
8. [Usage](#usage)
9. [Common Use Cases](#common-use-cases)
10. [Citing psyle](#citing-pysle)
11. [Acknowledgements](#acknowledgements)


## Documentation

Automatically generated pdocs can be found here:

http://timmahrt.github.io/pysle/

## Tutorials

There are tutorials available for learning how to use Pysle.  These
are in the form of IPython Notebooks which can be found in the /tutorials/
folder distributed with Pysle.

You can view them online using the external website Jupyter:

[Tutorial 1: Introduction to Pysle](<https://nbviewer.jupyter.org/github/timmahrt/pysle/blob/main/tutorials/tutorial1_intro_to_pysle.ipynb>)

[Tutorial 2: Pronunciationtools](<https://nbviewer.jupyter.org/github/timmahrt/pysle/blob/main/tutorials/tutorial2_pronunciationtools.ipynb>)

## Version History

*Pysle uses semantic versioning (Major.Minor.Patch)*

Please view [CHANGELOG.md](https://github.com/timmahrt/pysle/blob/main/CHANGELOG.md) for version history.


## Requirements

The following python modules are required.  They should be installed automatically but you can 
install them manually if you have any problems.
- [typing-extensions](`https://pypi.org/project/typing-extensions/`)
- [praatIO](<https://github.com/timmahrt/praatIO>) 

``Python 3.7.*`` or above

[Click here to visit travis-ci and see the specific versions of python that pysle is currently tested under](<https://app.travis-ci.com/github/timmahrt/pysle>)

If you are using ``Python 2.x`` or ``Python < 3.7``, you can use `Pysle 3.x`.

## ISLE Dictionary

pysle requires the ISLEdict pronunciation dictionary
(copyright Mark Hasegawa-Johnson, licensed under the MIT open source license).
This is bundled with psyle.  However, you may want to use a subset of the pronunciations
or you may want to add your own pronunciations.

In that case, please get the original file.

  [ISLEX github page](<https://github.com/uiuc-sst/g2ps>)

  [Direct link to the ISLEX file used in this project](<https://raw.githubusercontent.com/uiuc-sst/g2ps/master/English/ISLEdict.txt>) (ISLEdict.txt)

See `examples/isletool_examples.py` for an example of how to load a custom ISLEdict file.


## Installation

Pysle is on pypi and can be installed or upgraded from the command-line shell with pip like so

    python -m pip install pysle --upgrade

Otherwise, to manually install, after downloading the source from github, from a command-line shell, navigate to the directory containing setup.py and type

    python setup.py install

If python is not in your path, you'll need to enter the full path e.g.

    C:\Python36\python.exe setup.py install

## Upgrading

Please view [UPGRADING.md](https://github.com/timmahrt/pysle/blob/main/UPGRADING.md) for detailed information about how to upgrade from earlier versions.

## Usage

Here is a typical usage

```python
from pysle import isletool
isle = isletool.Isle()
print(isle.lookup('catatonic')[0].toList()) # Get the first entry's pronunciation
# >> [[['k', 'ˌæ'], ['ɾ', 'ə'], ['t', 'ˈɑ'], ['n', 'ɪ', 'k']]]
```

and another

```python
from pysle import isletool
from pysle import pronunciationtools

isle = isletool.Isle()

searchWord = 'another'
phoneList = ['n', 'ʌ', 'ð', 'ɚ']

returnList = pronunciationtools.findBestSyllabification(isle, searchWord, phoneList)
syllableList = returnList[2]
print(syllableList)
# >> [["''"], ['n', 'ʌ'], ['ð', 'ɚ']]
```

Please see \\examples for example usage


## Common Use Cases


What can you do with this library?

- look up the list of phones and syllables for canonical pronunciations
  of a word
    ```python
    isletool.LexicalTool('ISLEdict.txt').lookup('cat')
    ```

- map an actual pronunciation to a dictionary pronunciation (can be used
  to automatically find speech errors)
    ```python
    pronunciationtools.findClosestEntryForPhones(isleDict, 'cat', ['k', 'æ',])
    ```

- automatically syllabify a praat textgrid (see [praatIO](<https://github.com/timmahrt/praatIO>))
   containing words and phones (e.g. force-aligned text)
    ```python
    pysle.syllabifyTextgrid(isleDict, praatioTextgrid, "words", "phones")
    ```

## Citing pysle


Pysle is general purpose coding and doesn't need to be cited
(you should cite the
[ISLEX project](<http://www.isle.illinois.edu/speech_web_lg/data/g2ps/>)
instead) but if you would like to, it can be cited like so:

Tim Mahrt. Pysle. https://github.com/timmahrt/pysle, 2016.


## Acknowledgements


Development of Pysle was possible thanks to NSF grant **IIS 07-03624**
to Jennifer Cole and Mark Hasegawa-Johnson, NSF grant **BCS 12-51343**
to Jennifer Cole, José Hualde, and Caroline Smith, and
to the A*MIDEX project (n° **ANR-11-IDEX-0001-02**) to James Sneed German
funded by the Investissements d'Avenir French Government program, managed
by the French National Research Agency (ANR).
