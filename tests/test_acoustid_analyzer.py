import unittest
from mock import Mock, patch
from damn_at.analyzers.audio import acoustid_analyzer
from damn_at import mimetypes
import os


class TestCase(unittest.TestCase):

    def test_get_supported_mimetypes(self):
        mimetypes = acoustid_analyzer.get_supported_formats()
        if len(mimetypes) != 0:
            for mimetype in mimetypes:
                assert mimetype.startswith("audio/"), \
                    "acoustid_analyzer's handled_types error"
        else:
            assert False, "acoustid_analyzer's handled_types is empty"

    def test_analyzer(self):
        keys = ['duration', 'fingerprint_uuid', 'fingerprint']
        analyzer = acoustid_analyzer.SoundAnalyzer()
        uri = os.path.join(os.path.dirname(__file__),
                           '../../peragro-test-files/audio')
        for root, dirs, files in os.walk(uri):
            for file_name in files:
                path = os.path.join(root, file_name)
                mime = mimetypes.guess_type(path, False)[0]
                if mime.startswith('audio/'):
                    hello = analyzer.analyze(path)
                    if hello:
                        for asset in hello.assets:
                            for key, value in asset.metadata.items():
                                assert key in keys, \
                                    "Unknown key(feature):%s detected" % key
                    else:
                        assert False, \
                            "AcoustID analyzer failed with some error"


def test_suite():
    """Return a list of tests"""
    return unittest.TestLoader().loadTestsFromTestCase(TestCase)

if __name__ == '__main__':
    # unittest.main()
    unittest.TextTestRunner().run(test_suite())
