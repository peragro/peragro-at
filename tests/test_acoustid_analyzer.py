import unittest
import os
import tempfile

from mock import Mock, patch

from damn_at import bld
import damn_at.analyzers.audio.acoustid_analyzer as acoustid_analyzer

class TestCase(unittest.TestCase):

    def test_get_supported_mimetypes(self):
        mimetypes = acoustid_analyzer.get_supported_formats()
        if len(mimetypes) != 0:
            print (mimetypes)
            for mimetype in mimetypes:
                if mimetype.startswith("audio/"):
                    assert True
                else:
                    assert False

        else:
            assert False



def test_suite():
    """Return a list of tests"""
    return unittest.TestLoader().loadTestsFromTestCase(TestCase)

if __name__ == '__main__':
    #unittest.main()
    unittest.TextTestRunner().run(test_suite())