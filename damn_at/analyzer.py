"""
Role
====
Analyzer convience class to find the right plugin for a mimetype
and address it.
"""
import os
import sys

from metrology.instruments.gauge import Gauge

from . import registry
from .pluginmanager import DAMNPluginManagerSingleton
from .utilities import is_existing_file, calculate_hash_for_file, get_referenced_file_ids, abspath
from .metadatastore import MetaDataStore

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


class AnalyzerGauge(Gauge):
    """Gauge that returns the number of analyzer-plugins"""
    def __init__(self, analyzer):
        self.analyzer = analyzer
    def value(self):
        return len(self.analyzer.analyzers)


class Analyzer(object):
    """
    Analyze files and tries to find known assets types in it.
    """
    def __init__(self):
        registry.gauge('damn_at.analyzer.number_of_analyzers', AnalyzerGauge(self))
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
        :rtype: :py:class:`damn_at.thrift.generated.damn_types.ttypes.FileReference`
        :raises: AnalyzerException, AnalyzerFileException, AnalyzerUnknownTypeException
        """
        if not is_existing_file(an_uri):
            raise AnalyzerFileException('E: Analyzer: No such file "%s"!'%(an_uri))
        mimetype = mimetypes.guess_type(an_uri, False)[0]
        if mimetype in self.analyzers:
            file_ref = self.analyzers[mimetype].analyze(an_uri)
            return file_ref
        else:
            raise AnalyzerUnknownTypeException("E: Analyzer: No analyzer for %s (file: %s)"%(mimetype, an_uri))



def main():
    import logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    
    file_name = sys.argv[1]
    a = Analyzer()
    m = MetaDataStore()
    
    def hash_file_ref(file_ref):
        CACHE = {}
        def cached_calculate_hash_for_file(file_name):
            if file_name not in CACHE:
                path = abspath(file_name, file_ref)
                CACHE[file_name] = calculate_hash_for_file(path)
            return CACHE[file_name]
        file_ids = get_referenced_file_ids(file_ref)
        for file_id in file_ids:
            file_id.hash = cached_calculate_hash_for_file(file_id.filename)
        
    def analyze_file(file_name, file_ref=None):
        file_name = abspath(file_name, file_ref)
        hashid = calculate_hash_for_file(file_name)
        if m.is_in_store('/tmp/damn', hashid):
            print('Fetching from store...')
            ref = m.get_metadata('/tmp/damn', hashid)
            return ref, True
        else:
            print(a.get_supported_mimetypes())
            print('Analyzing file...')
            ref = a.analyze_file(file_name)
            hash_file_ref(ref)
            m.write_metadata('/tmp/damn', hashid, ref)
            return ref, False

    ref, from_store = analyze_file(file_name)

    file_ids = get_referenced_file_ids(ref)
    paths = set([x.filename for x in file_ids])
    for path in paths:
        if path != file_name:
            print('Analyzing', path)
            try:
                _, from_store = analyze_file(path, ref)
                print(_)
            except AnalyzerUnknownTypeException as e:
                print(e)

if __name__ == '__main__': 
    sys.argv[1] = '/home/sueastside/dev/blenderassets/cube1.blend'
    main()
