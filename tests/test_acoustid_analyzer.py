import unittest, os
from mock import Mock, patch
from damn_at.analyzers.audio import acoustid_analyzer
from damn_at import mimetypes
from damn_at import utilities


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
                    file_descr = analyzer.analyze(path)
                    if file_descr:
                        for asset in file_descr.assets:
                            for key, value in asset.metadata.items():
                                assert key in keys, \
                                    "Unknown key(feature):%s detected" % key
                    else:
                        assert False, \
                            "AcoustID analyzer failed with some error"

    def test_analyze_wavfile_(self):
        dic = {'fingerprint': "b'AQAAZImSbZqiLXDwKDSOC2JV9LiiHEcvCIcPHHYKHcd5-"
                              "Bry4UyCH4aPnhV-fMnx7EbZH1POI8d_8KaDPPOMS0YlmGlw"
                              "5oQPZj4ClXfAHlqHMDi-Hd98fGjCDomi9ELIi4ErYjru6Ao"
                              "6Tjv8o5KU6cJ3XD8azajMHE_-4TiO8PtgLoPyIFNRbUNv3A"
                              "jXgxeuHG-OWvkx5e3x4Bd0HblQTcFL4xyND_8JdC3yQ0f-o"
                              "OOJn_guC9_xo1ZOAKOcEIYBB0QRxgAAmAKEKuCAQQAwihwQ"
                              "ChFCCBAMCQXAIQQIpBAwCDhAFBCecCAIo4wgAhAhgDiGiGE"
                              "CMCAEI-hgBQACxhEhAA'",
               'fingerprint_uuid': 'd6b5ffe5-a332-554c-8a68-56eae6f9fbfe',
               'duration': '15.0044375s',
               'hello_world': 'sagar'}

        analyzer = acoustid_analyzer.SoundAnalyzer()
        uri = os.path.join(os.path.dirname(__file__),
                           '../../peragro-test-files/audio/wav/test.wav')
        file_descr = analyzer.analyze(uri)
        assert file_descr, "something went wrong while analysing test.wav"
        # print(file_descr)
        metadata_dic = {}
        for asset in file_descr.assets:
            for key, value in asset.metadata.items():
                ty, val = utilities.get_metadatavalue_type(value)
                metadata_dic[key] = val
        assert metadata_dic == dic, \
            "Analyzed values are not equal to the expected ones"


def test_suite():
    """Return a list of tests"""
    return unittest.TestLoader().loadTestsFromTestCase(TestCase)

if __name__ == '__main__':
    # unittest.main()
    unittest.TextTestRunner().run(test_suite())