# encoding: utf-8

from pysle import errors


def validateOption(variableName, value, optionClass):
    if value not in optionClass.validOptions:
        raise errors.WrongOption(variableName, value, optionClass.validOptions)
