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
    python_requires=">3.6.0",
    version="4.0.0",
    author="Tim Mahrt",
    author_email="timmahrt@gmail.com",
    url="https://github.com/timmahrt/pysle",
    package_dir={"pysle": "pysle"},
    packages=["pysle", "pysle.utilities"],
    package_data={
        "pysle": [
            "data/ISLEdict.txt",
        ]
    },
    install_requires=[
        "praatio >= 5.0",
        "typing_extensions",
    ],
    license="LICENSE",
    description=(
        "An interface to ISLEX, an IPA pronunciation dictionary "
        "for English with stress and syllable markings."
    ),
    long_description=io.open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
)
