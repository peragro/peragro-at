"""
Role
====
Transcoder convience class to find the right plugin for a mimetype
and address it.
"""
import os

from metrology.instruments.gauge import Gauge

from . import registry
from .pluginmanager import DAMNPluginManagerSingleton

from damn_at import TargetMimetype, TargetMimetypeOption
from .options import options_to_template, parse_options

from .utilities import find_asset_id_in_file_descr, get_asset_names_in_file_descr

from .mimetypes import guess_type


class TranscoderException(Exception):
    """Base Transcoder Exception"""
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return repr(self.msg)


class TranscoderFileException(TranscoderException):
    """Something wrong with the file"""
    pass
  

class TranscoderUnknownTypeException(TranscoderException):
    """Unknown type"""
    pass


class TranscoderGauge(Gauge):
    """Gauge that returns the number of transcoder-plugins"""
    def __init__(self, analyzer):
        self.analyzer = analyzer
    def value(self):
        return len(self.analyzer.analyzers)


class Transcoder(object):
    """
    Analyze files and tries to find known assets types in it.
    """
    def __init__(self):
        registry.gauge('damn_at.transcoder.number_of_transcoders', TranscoderGauge(self))
        self.transcoders = {}
        plugin_mgr = DAMNPluginManagerSingleton.get()

        for plugin in plugin_mgr.getPluginsOfCategory('Transcoder'):
            if plugin.plugin_object.is_activated:
                for src, _ in plugin.plugin_object.convert_map.items():
                    if not src in self.transcoders:
                        self.transcoders[src] = []
                    self.transcoders[src].append(plugin)
        
        self._build_target_mimetypes()
                    
    def _build_target_mimetypes(self):
        self.target_mimetypes = {}
        self.target_mimetypes_transcoders = {}
        for src_mimetype, transcoders in self.transcoders.items():
            for transcoder in transcoders:
                for dst_mimetype, options in transcoder.plugin_object.convert_map[src_mimetype].items():
                    tmt = TargetMimetype(mimetype=dst_mimetype, description=transcoder.description, template=options_to_template(options))
                    for option in options:
                        tmto = TargetMimetypeOption(name=option.name, 
                                                    description=option.description, 
                                                    type=option.type_description, 
                                                    constraint=option.constraint_description, 
                                                    default_value=option.default_description)
                        tmt.options.append(tmto)
                    if not src_mimetype in self.target_mimetypes:
                        self.target_mimetypes[src_mimetype] = []
                        self.target_mimetypes_transcoders[src_mimetype] = []
                    self.target_mimetypes[src_mimetype].append(tmt)
                    self.target_mimetypes_transcoders[src_mimetype].append((tmt, transcoder,))
 
    def _get_transcoder(self, src_mimetype, target_mimetype):
        """Returns a transcoder
        
        """
        target_mimetpes = self.target_mimetypes_transcoders[src_mimetype]
        for target, transcoder in target_mimetpes:
            if target == target_mimetype:
                return transcoder
                
                
    def get_target_mimetypes(self):
        """Returns a list of supported mimetypes, 'handled_types' of all analyzers
        
        :rtype: map<string, list<TargetMimetype>>
        """
        return self.target_mimetypes
        
    def get_target_mimetype(self, src_mimetype):
        """"""
        # TODO: Need some clever way to select the right transcoder in 
        # the list based on options passed.
        return self.target_mimetypes[src_mimetype][0] 
        
    def parse_options(self, src_mimetype, target_mimetype, **options):
        """"""
        transcoder = self._get_transcoder(src_mimetype, target_mimetype)
        convert_map_entry = transcoder.plugin_object.convert_map[src_mimetype][target_mimetype.mimetype]
        return parse_options(convert_map_entry, **options)

    def transcode(self, file_descr, asset_id, mimetype, **options):
        """Transcode the given AssetId in FileDescription to the specified mimetype 
        
        :rtype: list<string> file paths
        """
        src_mimetype = guess_type(file_descr.file.filename)[0]
        target_mimetype = self.get_target_mimetype(src_mimetype)
        transcoder = self._get_transcoder(src_mimetype, target_mimetype)
        
        return transcoder.plugin_object.transcode('/tmp/transcoded/', file_descr, asset_id, target_mimetype, **options)
        

def main():
    import sys
    from optparse import OptionParser
    import logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    
    from damn_at.metadatastore import MetaDataStore
    
    store_path = os.path.dirname(sys.argv[1])
    file_name = os.path.basename(sys.argv[1])
    asset_name = sys.argv[2]
    mime_type = sys.argv[3]
    
    m = MetaDataStore(store_path)
    t = Transcoder()
    
    target_mimetype = t.get_target_mimetype(mime_type)
    
    if not target_mimetype:
        raise TranscoderUnknownTypeException(mime_type+' needs to be one of '+str(t.get_target_mimetypes().keys()))

    
    from damn_at import _CMD_DESCRIPTION

    usage = "usage: %prog <store_path> <file_path> <mime_type> [options] " +_CMD_DESCRIPTION
    parser = OptionParser(usage=usage)
    for option in target_mimetype.options:
        parser.add_option("--"+option.name, dest=option.name, default=option.default_value, help='%s (%s) [default: %s]'%(option.description, option.constraint, option.default_value))

    (options, args) = parser.parse_args(sys.argv[3:])
    
    file_descr = m.get_metadata('', file_name)
            
    if asset_name not in get_asset_names_in_file_descr(file_descr):
        raise TranscoderFileException(asset_name+' not in file_descr '+str(get_asset_names_in_file_descr(file_descr)))
        
    asset_id = find_asset_id_in_file_descr(file_descr, asset_name)
    
    options = t.parse_options(mime_type, target_mimetype, **vars(options))
    
    print(_CMD_DESCRIPTION)
    print('Transcoding "%s"\n'%file_descr.file.filename)
    print('Using: %s'%target_mimetype.description)
    print('with: ')
    for option_name, option_value in options.items():
        print('* %s: %s '%(option_name, option_value))
    file_paths = t.transcode(file_descr, asset_id, mime_type, **options)
    print(file_paths)
    
    
if __name__ == '__main__': 
    main()
    #damn_at-transcode /tmp/damn/4bf0356127a51d7e2167433b7e78cedff3f8953a b2csmaterialpanel.png image/jpeg --size=128,128 -h
