import unittest

from mock import Mock, patch

from damn_at import mimetypes
from damn_at import utilities

from damn_at.pluginmanager import DAMNPluginManagerSingleton
from damn_at.transcoder import TranscoderException, Transcoder

from damn_at import FileDescription

class MockPlugin:
    def __init__(self, mimetype):
        self.plugin_object = type('Plugin', (object,), {})
        self.plugin_object.is_activated = True
        self.plugin_object.convert_map = {mimetype: {mimetype: []}}
        self.plugin_object.transcode = self.transcode
        self.description = 'description'

    def transcode(self, an_uri):
        return []


class MockDAMNPluginManager:
    def getPluginsOfCategory(self, cat):
        return [MockPlugin('some/mime'), MockPlugin('some/other')]

class TestCase(unittest.TestCase):
    """Test AnalyzerException"""
    def test_transcoder_exception(self):
        ex = TranscoderException('message')
        assert ex.msg == 'message'
        assert str(ex) == repr('message')

    """Test Analyzer"""
    @patch('damn_at.analyzer.mimetypes.guess_type')
    @patch('damn_at.analyzer.is_existing_file')
    @patch('damn_at.analyzer.os.stat')
    def test_transcoder_constructor(self, stat, is_existing_file, guess_type):
        guess_type.return_value = ['some/mime', None]
        is_existing_file.return_value = True
        mock = MockDAMNPluginManager()
        DAMNPluginManagerSingleton.get = classmethod(lambda x: mock)
        assert mock == DAMNPluginManagerSingleton.get()
        transcoder = Transcoder('dstpath')

        target_mimes = transcoder.get_target_mimetypes()

        assert 'some/mime' in target_mimes
        assert 'some/other' in target_mimes

        target_mime = transcoder.get_target_mimetype('some/mime', 'some/mime')
