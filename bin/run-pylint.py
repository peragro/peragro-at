#!/usr/bin/env python
"""Run pylint"""
import os

from pylint import lint

if __name__ == '__main__':
    directory = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(directory, '..', 'pylint.cfg')
    directory = os.path.join(directory, '../damn_at')
    lint.Run(list((directory, "--rcfile="+config_file, '--ignore=generated,b-script-*')))
