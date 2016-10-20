#!/usr/bin/env python
# encoding: utf-8
'''
Created on Oct 15, 2014

@author: tmahrt
'''
from setuptools import setup
import codecs
setup(name='pysle',
      version='1.4.0',
      author='Tim Mahrt',
      author_email='timmahrt@gmail.com',
      url='https://github.com/timmahrt/pysle',
      package_dir={'pysle':'pysle'},
      packages=['pysle'],
      license='LICENSE',
      long_description=codecs.open('README.rst', 'r', encoding="utf-8").read()
      )
