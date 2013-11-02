"""
Role
====
Analyzer convience class to find the right plugin for a mimetype
and address it.
"""

from .pluginmanager import DAMNPluginManagerSingleton
from .utilities import is_existing_file

from . import mimetypes


class AnalyzerException(Exception):
    """Base Analyzer Exception"""
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return repr(self.msg)
    
class AnalyzerFileException(AnalyzerException):
    """Something wrong with the file"""
    pass
  
class AnalyzerUnknownTypeException(AnalyzerException):
    """Unknown type"""
    pass


class Analyzer(object):
    """
    Analyze files and tries to find known assets types in it.
    """
    def __init__(self):
        self.analyzers = {}
        plugin_mgr = DAMNPluginManagerSingleton.get()

        for plugin in plugin_mgr.getPluginsOfCategory('Analyzer'):
            if plugin.plugin_object.is_activated:
                for mimetype in plugin.plugin_object.handled_types:
                    self.analyzers[mimetype] = plugin.plugin_object
    
    def get_supported_mimetypes(self):
        """Returns a list of supported mimetypes, 'handled_types' of all analyzers
        
        :rtype: list<string>
        """
        return self.analyzers.keys()
          
    def analyze_file(self, an_uri):
        """Returns a FileReference
        
        :param an_uri: the URI pointing to the file to be analyzed
        :rtype: :py:class:`damn_at.types.FileReference`
        :raises: AnalyzerException, AnalyzerFileException, AnalyzerUnknownTypeException
        """
        if not is_existing_file(an_uri):
            raise AnalyzerFileException('E: Analyzer: No such file "%s"!'%(an_uri))
        mimetype = mimetypes.guess_type(an_uri, False)[0]
        if mimetype in self.analyzers:
            file_ref = self.analyzers[mimetype].analyze(an_uri)
            return file_ref
        else:
            raise AnalyzerUnknownTypeException("E: Analyzer: No analyzer for %s (file: %s)"%(format, an_uri))
