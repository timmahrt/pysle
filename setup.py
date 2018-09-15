#!/usr/bin/env python
# encoding: utf-8
'''
Created on Oct 15, 2014

@author: tmahrt
'''
from setuptools import setup
import io
setup(name='pysle',
      version='1.5.7',
      author='Tim Mahrt',
      author_email='timmahrt@gmail.com',
      url='https://github.com/timmahrt/pysle',
      package_dir={'pysle':'pysle'},
      packages=['pysle'],
      license='LICENSE',
      description="An interface to ISLEX, an IPA pronunciation dictionary for English with stress and syllable markings.",
      long_description=io.open('README.rst', 'r', encoding="utf-8").read()
      )
