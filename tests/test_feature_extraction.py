import unittest
import os
from mock import Mock, patch
from damn_at.analyzers.audio import feature_extraction
from damn_at.analyzers.audio import acoustid_analyzer
from damn_at import mimetypes
from damn_at import utilities


class TestCase(unittest.TestCase):

    def test_get_supported_mimetypes(self):
        mimetypes = feature_extraction.get_supported_formats()
        if len(mimetypes) != 0:
            for mimetype in mimetypes:
                # print(mimetype)
                assert mimetype.startswith("audio/"), \
                    "feature_extraction's handled_types error"
        else:
            assert False, "feature_extraction's handled_types is empty"

    def test_analyzer(self):
        keys = ['bpm', 'beats_count', 'chord', 'key', 'average_loudness',
                'lossless', 'mood_party', 'genre_electronic', 'voice_instrumental',
                'mood_aggressive', 'ismir04_rhythm', 'mood_electronic', 'timbre',
                'danceability', 'genre_rosamerica', 'mood_relaxed', 'mood_acoustic',
                'moods_mirex', 'mood_happy', 'genre_tzanetakis', 'genre_dortmund',
                'mood_sad', 'gender', 'tonal_atonal']
        analyzer = feature_extraction.SoundAnalyzer()
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
                            "Feature extractor failed with some error"

    def test_analyze_wavfile_(self):
        dic = {'beats_count': '25.0', 'mood_acoustic': 'acoustic',
               'mood_party': 'not_party', 'moods_mirex': 'Cluster3',
               'lossless': 'True', 'danceability': 'not_danceable',
               'mood_aggressive': 'not_aggressive', 'key': 'F# minor',
               'gender': 'male', 'chord': 'C# minor',
               'voice_instrumental': 'instrumental', 'genre_tzanetakis': 'hip',
               'tonal_atonal': 'tonal', 'mood_happy': 'not_happy',
               'bpm': '95', 'mood_relaxed': 'relaxed',
               'genre_electronic': 'ambient', 'average_loudness': '0.909014284611',
               'genre_dortmund': 'alternative', 'mood_sad': 'sad',
               'mood_electronic': 'not_electronic', 'ismir04_rhythm': 'Waltz',
               'genre_rosamerica': 'cla', 'timbre': 'dark'}

        analyzer = feature_extraction.SoundAnalyzer()
        uri = os.path.join(os.path.dirname(__file__),
                           '../../peragro-test-files/audio/wav/test.wav')
        file_descr = analyzer.analyze(uri)
        assert file_descr, "something went wrong while analysing test.wav"
        # metadata_dic = {}
        for asset in file_descr.assets:
            for key, value in asset.metadata.items():
                ty, val = utilities.get_metadatavalue_type(value)
                # metadata_dic[key] = val
                assert dic[key] == val, \
                    "Analyzed value for key:%s is %s which is not equal " \
                    "to the expected one (%s)" % (key, val, dic[key])

    def test_analyze_mp3file_(self):
        dic = {'tonal_atonal': 'atonal', 'bpm': '128',
               'timbre': 'bright', 'mood_happy': 'not_happy',
               'genre_dortmund': 'electronic', 'gender': 'female',
               'mood_party': 'not_party', 'beats_count': '526.0',
               'mood_sad': 'not_sad', 'mood_aggressive': 'not_aggressive',
               'genre_electronic': 'trance', 'mood_relaxed': 'not_relaxed',
               'voice_instrumental': 'voice', 'average_loudness': '0.977689087391',
               'lossless': 'False', 'mood_acoustic': 'not_acoustic',
               'moods_mirex': 'Cluster5', 'chord': 'C major',
               'ismir04_rhythm': 'ChaChaCha', 'mood_electronic': 'electronic',
               'key': 'E major', 'genre_tzanetakis': 'jaz',
               'danceability': 'danceable', 'genre_rosamerica': 'rhy'}

        analyzer = feature_extraction.SoundAnalyzer()
        uri = os.path.join(os.path.dirname(__file__),
                           '../../peragro-test-files/audio/mp3/test.mp3')
        file_descr = analyzer.analyze(uri)
        assert file_descr, "something went wrong while analysing test.mp3"
        # metadata_dic = {}
        for asset in file_descr.assets:
            for key, value in asset.metadata.items():
                ty, val = utilities.get_metadatavalue_type(value)
                # metadata_dic[key] = val
                assert dic[key] == val, \
                    "Analyzed value for key:%s is %s which is not equal " \
                    "to the expected one (%s)" % (key, val, dic[key])

    def test_analyze_flacfile_(self):
        dic = {'tonal_atonal': 'atonal', 'bpm': '139',
               'timbre': 'dark', 'mood_happy': 'happy',
               'genre_dortmund': 'raphiphop', 'gender': 'female',
               'mood_party': 'not_party', 'beats_count': '15.0',
               'mood_sad': 'not_sad', 'mood_aggressive': 'not_aggressive',
               'genre_electronic': 'dnb', 'mood_relaxed': 'relaxed',
               'voice_instrumental': 'instrumental', 'average_loudness': '0.982675015926',
               'lossless': 'True', 'mood_acoustic': 'not_acoustic',
               'moods_mirex': 'Cluster5', 'chord': 'E major',
               'ismir04_rhythm': 'Samba', 'mood_electronic': 'electronic',
               'key': 'G# minor', 'genre_tzanetakis': 'jaz',
               'danceability': 'not_danceable', 'genre_rosamerica': 'hip'}

        analyzer = feature_extraction.SoundAnalyzer()
        uri = os.path.join(os.path.dirname(__file__),
                           '../../peragro-test-files/audio/flac/dubstep.flac')
        file_descr = analyzer.analyze(uri)
        assert file_descr, "something went wrong while analysing dubstep.flac"
        # metadata_dic = {}
        for asset in file_descr.assets:
            for key, value in asset.metadata.items():
                ty, val = utilities.get_metadatavalue_type(value)
                # metadata_dic[key] = val
                assert dic[key] == val, \
                    "Analyzed value for key:%s is %s which is not equal " \
                    "to the expected one (%s)" % (key, val, dic[key])

    def test_analyze_oggfile_(self):
        dic = {'tonal_atonal': 'atonal', 'bpm': '139',
               'timbre': 'dark', 'mood_happy': 'happy',
               'genre_dortmund': 'raphiphop', 'gender': 'female',
               'mood_party': 'not_party', 'beats_count': '15.0',
               'mood_sad': 'not_sad', 'mood_aggressive': 'not_aggressive',
               'genre_electronic': 'dnb', 'mood_relaxed': 'relaxed',
               'voice_instrumental': 'instrumental', 'average_loudness': '0.982675015926',
               'lossless': 'True', 'mood_acoustic': 'not_acoustic',
               'moods_mirex': 'Cluster5', 'chord': 'E major',
               'ismir04_rhythm': 'Samba', 'mood_electronic': 'electronic',
               'key': 'G# minor', 'genre_tzanetakis': 'jaz',
               'danceability': 'not_danceable', 'genre_rosamerica': 'hip'}

        analyzer = feature_extraction.SoundAnalyzer()
        uri = os.path.join(os.path.dirname(__file__),
                           '../../peragro-test-files/audio/flac/dubstep.flac')
        file_descr = analyzer.analyze(uri)
        assert file_descr, "something went wrong while analysing dubstep.flac"
        # metadata_dic = {}
        for asset in file_descr.assets:
            for key, value in asset.metadata.items():
                ty, val = utilities.get_metadatavalue_type(value)
                # metadata_dic[key] = val
                assert dic[key] == val, \
                    "Analyzed value for key:%s is %s which is not equal " \
                    "to the expected one (%s)" % (key, val, dic[key])


def test_suite():
    """Return a list of tests"""
    return unittest.TestLoader().loadTestsFromTestCase(TestCase)

if __name__ == '__main__':
    # unittest.main()
    unittest.TextTestRunner().run(test_suite())
