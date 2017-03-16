"""
Role
====
Analyzer convience class to find the right plugin for a mimetype
and address it.
"""
import os
if os.name == 'nt':

    class Pwd():
        def getpwuid(self, user):
            pass
    pwd = Pwd()
    class Grp():
        def getgrgid(self, user):
            pass
    grp = Grp()
else:
    import pwd
    import grp    
import time
from datetime import datetime

from damn_at import MetaDataValue, MetaDataType
from damn_at.pluginmanager import DAMNPluginManagerSingleton
from damn_at.utilities import (
    is_existing_file,
    calculate_hash_for_file,
    get_referenced_file_ids,
    abspath,
    get_metadatavalue_type
)
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
                    analyzer = self.analyzers.setdefault(mimetype, [])
                    if plugin not in analyzer:
                        analyzer.append(plugin)

    def get_supported_mimetypes(self):
        """Returns a list of supported mimetypes, 'handled_types' of all analyzers

        :rtype: list<string>
        """
        return self.analyzers.keys()

    def get_supported_metadata(self):
        """Returns a list of supported metada, per mimetype.

        :rtype: map<string, list<tuple<string,MetaDataType>>>
        """
        import imp, inspect  # noqa
        from damn_at.metadata import MetaDataExtractor

        metadata = {}
        for mimetype, analyzer in self.analyzers.items():
            try:
                module = imp.load_source('damn_at.metadata.' + (mimetype.replace('.', '__')), os.path.join(os.path.dirname(analyzer.path), 'metadata.py'))
                for name in dir(module):
                    cls = getattr(module, name)
                    if inspect.isclass(cls) and not MetaDataExtractor == cls and issubclass(cls, MetaDataExtractor):
                        if hasattr(cls, '__mimetype__'):
                            metadata[cls.__mimetype__] = cls.fields()
                        else:
                            for mimetype in analyzer.plugin_object.handled_types:
                                metadata[mimetype] = cls.fields()
            except IOError:
                pass
        return metadata

    def _file_metadata(self, an_uri, file_descr):
        """Get metadata about the actual file and add it to the FileDescription
        """
        def convert_time(st_time):
            dt = datetime.fromtimestamp(stat.st_mtime)
            return dt.isoformat()

        stat = os.stat(an_uri)
        if file_descr.metadata is None:
            file_descr.metadata = {}
        file_descr.metadata['pw_name'] = MetaDataValue(type=MetaDataType.STRING, string_value=pwd.getpwuid(stat.st_uid).pw_name)
        file_descr.metadata['gr_name'] = MetaDataValue(type=MetaDataType.STRING, string_value=grp.getgrgid(stat.st_gid).gr_name)
        file_descr.metadata['st_size'] = MetaDataValue(type=MetaDataType.INT, int_value=stat.st_size)

        file_descr.metadata['st_ctime'] = MetaDataValue(type=MetaDataType.STRING, string_value=convert_time(stat.st_ctime))
        file_descr.metadata['st_mtime'] = MetaDataValue(type=MetaDataType.STRING, string_value=convert_time(stat.st_mtime))

        #TODO:
        try:
            from damn_at.repository import Repository
            repo = Repository('/home/sueastside/dev/DAMN/damn-test-files')

            repo.get_meta_data(an_uri, file_descr)
        except Exception as repo_exception:
            logger.debug("Unable to extract repository information: %s", str(repo_exception))

    def _append_metadata(self, orig_metadata, new_metadata):
        for key, value in new_metadata.items():
            if key not in orig_metadata:
                orig_metadata[key] = value

    def _combine_assets(self, orig_descr, new_descr):
        orig_assets = dict(((asset.asset.mimetype, asset.asset.subname), asset) for asset in orig_descr.assets)
        for asset in new_descr.assets:
            orig_asset = orig_assets.get((asset.asset.mimetype, asset.asset.subname), None)
            if orig_asset:
                self._append_metadata(orig_asset.metadata, asset.metadata)
            else:
                orig_descr.assets.append(asset)

    def analyze_file(self, an_uri):
        """Returns a FileDescription

        :param an_uri: the URI pointing to the file to be analyzed
        :rtype: :py:class:`damn_at.FileDescription`
        :raises: AnalyzerException, AnalyzerFileException, AnalyzerUnknownTypeException
        """
        if not is_existing_file(an_uri):
            raise AnalyzerFileException('E: Analyzer: No such file "%s"!' % (an_uri))
        mimetype = mimetypes.guess_type(an_uri, False)[0]
        if mimetype in self.analyzers:
            try:
                file_descr = None
                for analyzer in self.analyzers[mimetype]:
                    if not file_descr:
                        file_descr = analyzer.plugin_object.analyze(an_uri)
                        file_descr.mimetype = mimetype
                    else:
                        self._combine_assets(file_descr, analyzer.plugin_object.analyze(an_uri))
                self._file_metadata(an_uri, file_descr)
                return file_descr
            except Exception as ex:
                import traceback
                traceback.print_exc()
                raise AnalyzerException("E: Failed to analyze %s because of %s" % (an_uri, str(ex)))
        else:
            raise AnalyzerUnknownTypeException("E: Analyzer: No analyzer for %s (file: %s)" % (mimetype, an_uri))

'''
def analyze(analyzer, metadatastore, file_name, output, forcereanalyze=False):
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
        if not forcereanalyze and metadatastore.is_in_store('/tmp/damn', hashid):
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
        output.info('\n%s %s' % (descr.file.hash, '(From store)' if from_store else ''))
        output.info('-' * 40)
        output.info('Assets: %d', len(descr.assets))
        for asset in descr.assets:
            output.info('  -->%s  (%s)' % (asset.asset.subname, asset.asset.mimetype))
            if asset.metadata:
                for key, val in asset.metadata.items():
                    item_type, val = get_metadatavalue_type(val)
                    output.info('    - %s  %s (%s)' % (key, val, item_type))

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

    import sys
    import argparse
    import logging

    from damn_at import _CMD_DESCRIPTION

    analyzer = Analyzer()

    epilog = _CMD_DESCRIPTION + '\nSupported mimetypes: \n'
    for mime, meta in analyzer.get_supported_metadata().items():
        epilog += ' * %s:\n' % mime
        for key, item_type in meta:
            epilog += '   - %s (%s)\n' % (key, item_type)

    #Process the positional arguments
    parser = argparse.ArgumentParser(epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument('metadatastore', help='path to the metadata store')
    parser.add_argument('path', help='path to a file or a directory to analyze recursively')
    parser.add_argument('--force', action='store_true', help='foo the bars before frobbling')
    parser.add_argument(
        '-d',
        '--debug',
        help='Print lots of debugging statements',
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.WARNING
    )
    parser.add_argument(
        '-v',
        '--verbose',
        help='Be verbose',
        action="store_const",
        dest="loglevel",
        const=logging.INFO
    )

    if len(sys.argv) < 2:
        parser.print_help()
        parser.exit(1)

    args = parser.parse_args()

    logging.basicConfig(format='%(levelname)s:%(message)s', level=args.loglevel)
    formatter = logging.Formatter('%(message)s')
    output = logging.getLogger('damn-at_analyzer')
    stream_handler = logging.StreamHandler()
    output.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    output.propagate = False
    output.handlers = []
    output.addHandler(stream_handler)

    output.info('-' * 70)
    output.info('Analyzing %s into %s', args.path, args.metadatastore)
    output.info('%s', '(using cache if available)' if not args.force else '(ignoring cache)')
    output.info('-' * 70)
    analyzer = Analyzer()
    metadatastore = MetaDataStore(args.metadatastore)

    if os.path.isfile(args.path):
        analyze(analyzer, metadatastore, os.path.abspath(args.path), output, forcereanalyze=args.force)
    elif os.path.isdir(args.path):
        for root, dirs, files in os.walk(args.path):
            if '.git' in dirs:
                dirs.remove('.git')
            for file_name in files:
                if not file_name.startswith('.'):
                    try:
                        analyze(analyzer, metadatastore, os.path.join(root, file_name), output)
                    except AnalyzerUnknownTypeException as aute:
                        logger.warn("Unknown type exception: %s", str(aute))
    else:
        logger.warn("No such file: %s", args.path)


if __name__ == '__main__':
    main()
'''
