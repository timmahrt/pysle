#!/usr/bin/env python
# encoding: utf-8
'''
Created on Oct 15, 2014

@author: tmahrt
'''
from distutils.core import setup
setup(name='pysle',
      version='1.3.0',
      author='Tim Mahrt',
      author_email='timmahrt@gmail.com',
      package_dir={'pysle':'pysle'},
      packages=['pysle'],
      license='LICENSE',
      long_description=open('README.rst', 'r').read(),
#       install_requires=[], # No requirements! # requires 'from setuptools import setup'
      )
