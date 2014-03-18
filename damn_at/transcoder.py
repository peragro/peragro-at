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
    def __init__(self, path):
        self._path = path
        #registry.gauge('damn_at.transcoder.number_of_transcoders', TranscoderGauge(self))
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
        target_mimetypes = self.target_mimetypes_transcoders[src_mimetype]
        for target, transcoder in target_mimetypes:
            if target == target_mimetype:
                return transcoder
                
                
    def get_target_mimetypes(self):
        """Returns a list of supported mimetypes, 'handled_types' of all analyzers
        
        :rtype: map<string, list<TargetMimetype>>
        """
        return self.target_mimetypes
        
    def get_target_mimetype(self, src_mimetype, mimetype, **options):
        """"""
        # TODO: Need some clever way to select the right transcoder in 
        # the list based on options passed.
        if src_mimetype in self.target_mimetypes_transcoders:
            target_mimetypes = self.target_mimetypes_transcoders[src_mimetype]
            for target, transcoder in target_mimetypes:
                if target.mimetype == mimetype:
                    return target
        
    def parse_options(self, src_mimetype, target_mimetype, **options):
        """"""
        transcoder = self._get_transcoder(src_mimetype, target_mimetype)
        convert_map_entry = transcoder.plugin_object.convert_map[src_mimetype][target_mimetype.mimetype]
        return parse_options(convert_map_entry, **options)
        
    def get_paths(self, asset_id, target_mimetype, **options):
        """"""
        transcoder = self._get_transcoder(asset_id.mimetype, target_mimetype)
        convert_map_entry = transcoder.plugin_object.convert_map[asset_id.mimetype][target_mimetype.mimetype]
        
        path_templates = []
        single_options = dict([(option.name, option) for option in convert_map_entry if not option.is_array])
        single_options = dict([(option, value) for option, value in options.items() if option in single_options])
        array_options = dict([(option.name, option) for option in convert_map_entry if option.is_array])
        array_options = dict([(option, value) for option, value in options.items() if option in array_options])
        
        from damn_at.options import expand_path_template
        path_template = expand_path_template(target_mimetype.template, target_mimetype.mimetype, asset_id, **single_options)
        
        #TODO: does not work for multiple arrays.
        if len(array_options):
            for key, values in array_options.items():
                from string import Template
                for value in values:
                    t = Template(path_template)
                    file_path = t.safe_substitute(**{key:value})
                    path_templates.append(file_path)
        else:
            path_templates.append(path_template)
        
        #print path_template
        #print path_templates
        return path_templates

    def transcode(self, file_descr, asset_id, mimetype, **options):
        """Transcode the given AssetId in FileDescription to the specified mimetype 
        
        :rtype: list<string> file paths
        """
        target_mimetype = self.get_target_mimetype(asset_id.mimetype, mimetype)
        transcoder = self._get_transcoder(asset_id.mimetype, target_mimetype)
        
        return transcoder.plugin_object.transcode(self._path, file_descr, asset_id, target_mimetype, **options)
        

def main():
    import sys
    import argparse
    import logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    
    from damn_at.metadatastore import MetaDataStore
    from damn_at import _CMD_DESCRIPTION
    
    t = Transcoder('/tmp/transcoded/')
    
    epilog='Supported mimetypes: \n'
    for mime, targets in t.get_target_mimetypes().items():
        epilog +=' * %s -> %s \n'%(mime, str(map(lambda x: x.mimetype, targets)))

    #Process the positional arguments
    parser = argparse.ArgumentParser(add_help=False, epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument('path')
    parser.add_argument('assetname')
    parser.add_argument('mimetype')
    
    try:
        args = parser.parse_args(sys.argv[1:4])
    except:
        parser.print_help()
        sys.exit(1)
        
    store_path = os.path.dirname(args.path)
    file_name = os.path.basename(args.path)
    
    m = MetaDataStore(store_path)
    
    
    file_descr = m.get_metadata('', file_name)

    if args.assetname not in get_asset_names_in_file_descr(file_descr):
        raise TranscoderFileException(args.assetname+' not in file_descr '+str(get_asset_names_in_file_descr(file_descr)))
        
    asset_id = find_asset_id_in_file_descr(file_descr, args.assetname)
    
    target_mimetype = t.get_target_mimetype(asset_id.mimetype, args.mimetype)
    
    if not target_mimetype:
        if asset_id.mimetype not in t.get_target_mimetypes():
            raise TranscoderUnknownTypeException(asset_id.mimetype+' needs to be one of '+str(t.get_target_mimetypes().keys()))
        else:
            targets = [x.mimetype for x in t.get_target_mimetypes()[asset_id.mimetype]]
            raise TranscoderUnknownTypeException(args.mimetype+' needs to be one of '+str(targets))
    
    #Process the optional arguments
    parser = argparse.ArgumentParser()    
    for option in target_mimetype.options:
        parser.add_argument("--"+option.name, dest=option.name, default=option.default_value, help='%s (%s) [default: %s]'%(option.description, option.constraint, option.default_value))

    options = parser.parse_args(sys.argv[4:])
    
    # Parse the options using the convert_map of the transcoder
    options = t.parse_options(asset_id.mimetype, target_mimetype, **vars(options))
    
    print(_CMD_DESCRIPTION)
    print('Transcoding "%s"\n'%file_descr.file.filename)
    print('Using: %s'%target_mimetype.description)
    print('with: ')
    for option_name, option_value in options.items():
        print('* %s: %s '%(option_name, option_value))
    file_paths = t.transcode(file_descr, asset_id, args.mimetype, **options)
    print(file_paths)
    
    
if __name__ == '__main__': 
    main()
    #damn_at-transcode /tmp/damn/4bf0356127a51d7e2167433b7e78cedff3f8953a b2csmaterialpanel.png image/jpeg --size=128,128 -h
