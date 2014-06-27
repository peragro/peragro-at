"""
Does some stuff
"""
import os
import unittest

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

from damn_at.pluginmanager import DAMNPluginManagerSingleton
from damn_at.transcoder import Transcoder


class TestCase(unittest.TestCase):
    """Test case"""
    def test_get_target_mimetypes(self):
        """Test"""
        mimetypes = Transcoder('/tmp').get_target_mimetypes()
        for src, dst in mimetypes.items():
            print(src, dst)
        assert True


def test_suite():
    """Return a list of tests"""
    return unittest.TestLoader().loadTestsFromTestCase(TestCase)

if __name__ == '__main__':
    #unittest.main()
    unittest.TextTestRunner().run(test_suite())
