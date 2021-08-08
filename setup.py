#!/usr/bin/env python
# encoding: utf-8
"""
Created on Oct 15, 2014

@author: tmahrt
"""
import io
from setuptools import setup

setup(
    name="pysle",
    version="2.3.1",
    author="Tim Mahrt",
    author_email="timmahrt@gmail.com",
    url="https://github.com/timmahrt/pysle",
    package_dir={"pysle": "pysle"},
    packages=["pysle"],
    package_data={
        "pysle": [
            "data/ISLEdict.txt",
        ]
    },
    license="LICENSE",
    description="An interface to ISLEX, an IPA pronunciation dictionary "
    "for English with stress and syllable markings.",
    install_requires=["praatio ~= 4.1"],
    long_description=io.open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
)
