"""Run pylint"""
import os
import unittest

from pylint import lint

class PyLint(unittest.TestCase):
    """Run pylint"""
    def test_pylint(self):
        """Run pylint"""
        directory = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(directory, '..', 'pylint.cfg')
        directory = os.path.join(directory, '../damn_at')
        lint.Run(list((directory, "--rcfile="+config_file, )), exit=False)
        assert True


