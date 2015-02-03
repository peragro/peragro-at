import unittest

from mock import Mock, patch

from damn_at import mimetypes
from damn_at import utilities

from damn_at.pluginmanager import DAMNPluginManagerSingleton
from damn_at.analyzer import AnalyzerException, Analyzer

from damn_at import FileDescription

class MockPlugin:
    def __init__(self, mimetype):
        self.plugin_object = type('Plugin', (object,), {})
        self.plugin_object.is_activated = True
        self.plugin_object.handled_types = [mimetype]
        self.plugin_object.analyze = self.analyze

    def analyze(self, an_uri):
        return FileDescription()


class MockDAMNPluginManager:
    def getPluginsOfCategory(self, cat):
        return [MockPlugin('some/mime'), MockPlugin('some/other')]

class TestCase(unittest.TestCase):
    """Test AnalyzerException"""
    def test_analyzer_exception(self):
        ex = AnalyzerException('message')
        assert ex.msg == 'message'
        assert str(ex) == repr('message')

    """Test Analyzer"""
    @patch('damn_at.analyzer.mimetypes.guess_type')
    @patch('damn_at.analyzer.is_existing_file')
    @patch('damn_at.analyzer.os.stat')
    def test_analyzer_constructor(self, stat, is_existing_file, guess_type):
        guess_type.return_value = ['some/mime', None]
        is_existing_file.return_value = True
        mock = MockDAMNPluginManager()
        DAMNPluginManagerSingleton.get = classmethod(lambda x: mock)
        assert mock == DAMNPluginManagerSingleton.get()
        analyzer = Analyzer()

        mime_types = analyzer.get_supported_mimetypes()
        assert 'some/mime' in mime_types
        assert 'some/other' in mime_types

        descr = analyzer.analyze_file('somefakefile')
        assert descr is not None

        is_existing_file.return_value = False
        self.assertRaises(AnalyzerException, analyzer.analyze_file, 'somefakefile')


        is_existing_file.return_value = True
        guess_type.return_value = ['mime/thatwedonthave', None]
        self.assertRaises(AnalyzerException, analyzer.analyze_file, 'somefakefile')
