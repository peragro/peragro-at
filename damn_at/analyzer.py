"""
Role
====
Analyzer convience class to find the right plugin for a mimetype
and address it.
"""
import os
import sys
import pwd
import grp
import time

from metrology.instruments.gauge import Gauge

from damn_at import registry, MetaDataValue, MetaDataType
from damn_at.pluginmanager import DAMNPluginManagerSingleton
from damn_at.utilities import is_existing_file, calculate_hash_for_file, get_referenced_file_ids, abspath
from damn_at.metadatastore import MetaDataStore

from damn_at import mimetypes
from damn_at import logger

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
        #registry.gauge('damn_at.analyzer.number_of_analyzers', AnalyzerGauge(self))
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
        
    def _file_metadata(self, an_uri, file_descr):
        """Get metadata about the actual file and add it to the FileDescription
        """
        stat = os.stat(an_uri)
        if file_descr.metadata is None:
            file_descr.metadata = {}
        file_descr.metadata['pw_name'] = MetaDataValue(type=MetaDataType.STRING, string_value=pwd.getpwuid(stat.st_uid).pw_name)
        file_descr.metadata['gr_name'] = MetaDataValue(type=MetaDataType.STRING, string_value=grp.getgrgid(stat.st_gid).gr_name)
        file_descr.metadata['st_size'] = MetaDataValue(type=MetaDataType.INT, int_value=stat.st_size)
        
        file_descr.metadata['st_ctime'] = MetaDataValue(type=MetaDataType.STRING, string_value=time.asctime(time.localtime(stat.st_ctime)))
        file_descr.metadata['st_mtime'] = MetaDataValue(type=MetaDataType.STRING, string_value=time.asctime(time.localtime(stat.st_mtime)))
        
        #TODO:
        try:
            from damn_at.repository import Repository
            repo = Repository('/home/sueastside/dev/DAMN/damn-test-files')
            
            repo.get_meta_data(an_uri, file_descr)
        except Exception as repo_exception:
            logger.warn("Unable to extract repository information: %s", str(repo_exception))
          
    def analyze_file(self, an_uri):
        """Returns a FileDescription
        
        :param an_uri: the URI pointing to the file to be analyzed
        :rtype: :py:class:`damn_at.FileDescription`
        :raises: AnalyzerException, AnalyzerFileException, AnalyzerUnknownTypeException
        """
        if not is_existing_file(an_uri):
            raise AnalyzerFileException('E: Analyzer: No such file "%s"!'%(an_uri))
        mimetype = mimetypes.guess_type(an_uri, False)[0]
        if mimetype in self.analyzers:
            file_descr = self.analyzers[mimetype].analyze(an_uri)
            file_descr.mimetype = mimetype
            self._file_metadata(an_uri, file_descr)
            return file_descr
        else:
            raise AnalyzerUnknownTypeException("E: Analyzer: No analyzer for %s (file: %s)"%(mimetype, an_uri))


def analyze(analyzer, metadatastore, file_name, output):
    """TODO: move hashing to generic function and metadatastore usage to the metadatastore module. """
    def hash_file_descr(file_descr):
        """Calculate the hashes for all FileIds in a given FileDescription"""
        CACHE = {}
        def cached_calculate_hash_for_file(file_name):
            """Calculate and cache the hash for a given file"""
            if file_name not in CACHE:
                path = abspath(file_name, file_descr)
                CACHE[file_name] = calculate_hash_for_file(path)
            return CACHE[file_name]
        file_ids = get_referenced_file_ids(file_descr)
        for file_id in file_ids:
            file_id.hash = cached_calculate_hash_for_file(file_id.filename)
        
    def analyze_file(file_name, file_descr=None):
        """Analyze or fetch from metadatastorage a given filename"""
        file_name = abspath(file_name, file_descr)

        hashid = calculate_hash_for_file(file_name)
        if metadatastore.is_in_store('/tmp/damn', hashid):
            #print('Fetching from store...%s'%(hashid))
            descr = metadatastore.get_metadata('/tmp/damn', hashid)
            return descr, True
        else:
            #print('Analyzing...')
            descr = analyzer.analyze_file(file_name)
            hash_file_descr(descr)
            metadatastore.write_metadata('/tmp/damn', hashid, descr)
            return descr, False
    
    descr, from_store = analyze_file(file_name)
    if descr.assets:
        output.info('\n%s %s'%(descr.file.hash, '(From store)' if from_store else '' ))
        output.info('-'*40)
        output.info('Assets: %d', len(descr.assets))
        for asset in descr.assets:
            output.info('  -->%s  (%s)'%(asset.asset.subname, asset.asset.mimetype))

    file_ids = get_referenced_file_ids(descr)
    paths = set([x.filename for x in file_ids])
    for path in paths:
        if path != file_name:
            #print('Analyzing', path, file_name)
            try:
                _, from_store = analyze_file(path, descr)
                #print(_)
            except AnalyzerUnknownTypeException as aute:
                logger.warn("Unknown type exception: %s", str(aute))
            except AnalyzerFileException as afe:
                logger.warn("No such file: %s", str(afe))
    
    return descr

def main():
    """Main function"""
    import logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    
    formatter = logging.Formatter('%(message)s')
    output = logging.getLogger('damn-at_analyzer')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    output.propagate = False
    output.handlers = []
    output.addHandler(stream_handler)
    
    store_path = sys.argv[1]
    file_name = sys.argv[2]
    output.info('-'*70)
    output.info('Analyzing %s into %s', file_name, store_path)
    output.info('-'*70)
    analyzer = Analyzer()
    metadatastore = MetaDataStore(store_path)
    
    if os.path.isfile(file_name):
        analyze(analyzer, metadatastore, os.path.abspath(file_name), output)
    else:
        for root, dirs, files in os.walk(file_name):
            if '.git' in dirs:
                dirs.remove('.git')
            for file_name in files:
                if not file_name.startswith('.'):
                    try:
                        analyze(analyzer, metadatastore, os.path.join(root, file_name), output)
                    except AnalyzerUnknownTypeException as aute:
                        logger.warn("Unknown type exception: %s", str(aute))
    
    

if __name__ == '__main__': 
    main()
