import unittest
from mock import Mock, patch
from damn_at.analyzers.audio import acoustid_analyzer


class TestCase(unittest.TestCase):

    def test_get_supported_mimetypes(self):
        mimetypes = acoustid_analyzer.get_supported_formats()
        if len(mimetypes) != 0:
            # print(mimetypes)
            for mimetype in mimetypes:
                assert mimetype.startswith("audio/"), \
                    "acoustid_analyzer's handled_types error"
        else:
            assert False, "acoustid_analyzer's handled_types is empty"


def test_suite():
    """Return a list of tests"""
    return unittest.TestLoader().loadTestsFromTestCase(TestCase)

if __name__ == '__main__':
    # unittest.main()
    unittest.TextTestRunner().run(test_suite())
