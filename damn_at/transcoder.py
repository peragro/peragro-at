"""
Role
====
Transcoder convience class to find the right plugin for a mimetype
and address it.
"""
import os

from .pluginmanager import DAMNPluginManagerSingleton

from damn_at import TargetMimetype, TargetMimetypeOption
from .options import options_to_template, parse_options

from .utilities import find_asset_ids_in_file_descr, get_asset_names_in_file_descr

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

class TranscoderUnknownAssetException(TranscoderException):
    """Unknown asset"""
    pass

class Transcoder(object):
    """
    Analyze files and tries to find known assets types in it.
    """
    def __init__(self, path):
        self._path = path
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
    
    
    from damn_at.metadatastore import MetaDataStore
    from damn_at import _CMD_DESCRIPTION
    
    t = Transcoder('/tmp/transcoded/')
    
    epilog = 'Supported mimetypes: \n'
    for mime, targets in t.get_target_mimetypes().items():
        epilog +=' * %s -> %s \n'%(mime, str(map(lambda x: x.mimetype, targets)))

    #Process the positional arguments
    parser = argparse.ArgumentParser(add_help=False, epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument('path', help='The path to the FileDescription file')
    parser.add_argument('assetname', help='The subname of the asset to transcoder')
    parser.add_argument('mimetype', help='The destination mimetype')
    parser.add_argument('-d','--debug',
        help='Print lots of debugging statements',
        action="store_const",dest="loglevel",const=logging.DEBUG,
        default=logging.WARNING
    )
    parser.add_argument('-v','--verbose',
        help='Be verbose',
        action="store_const",dest="loglevel",const=logging.INFO
    )
    
    try:
        args, options_args = parser.parse_known_args()
    except:
        parser.print_help()
        parser.exit(1)
        
    logging.basicConfig(format='%(levelname)s:%(message)s', level=args.loglevel)
        
    store_path = os.path.dirname(args.path)
    file_name = os.path.basename(args.path)
    
    m = MetaDataStore(store_path)
    
    
    file_descr = m.get_metadata('', file_name)

    import re
    
    regexp = re.compile(r'^(.+?)(\((.+?)\))?$') 
    match = regexp.match(args.assetname)  
    
    asset_subname = match.group(1)
    asset_mimetype = match.group(3)
    
    
    if asset_subname not in get_asset_names_in_file_descr(file_descr):
        raise TranscoderUnknownAssetException(asset_subname+' not in file_descr '+str(get_asset_names_in_file_descr(file_descr)))
        
    asset_ids = find_asset_ids_in_file_descr(file_descr, asset_subname)
    
    if len(asset_ids) == 1:
        asset_id = asset_ids[0]
    elif asset_mimetype:
        nasset_ids = [asset_id for asset_id in asset_ids if asset_id.mimetype == asset_mimetype]
        if len(nasset_ids) == 1:
            asset_id = nasset_ids[0]
        else:
            assets = ['%s(%s)'%(asset_id.subname, asset_id.mimetype) for asset_id in asset_ids]
            raise TranscoderUnknownAssetException(args.assetname+' not in file_descr. Please specify one of %s'%(assets)) 
    else:
        mimes = [asset_id.mimetype for asset_id in asset_ids]
        raise TranscoderUnknownAssetException(asset_subname+' ambigious in file_descr. Please specify "%s(<mimetype>)" with <mimetype> one of %s'%(asset_subname, mimes)) 
    
    target_mimetype = t.get_target_mimetype(asset_id.mimetype, args.mimetype)
    
    if not target_mimetype:
        if asset_id.mimetype not in t.get_target_mimetypes():
            raise TranscoderUnknownTypeException(asset_id.mimetype+' needs to be one of '+str(t.get_target_mimetypes().keys()))
        else:
            targets = [x.mimetype for x in t.get_target_mimetypes()[asset_id.mimetype]]
            raise TranscoderUnknownTypeException(args.mimetype+' needs to be one of '+str(targets))
    
    #Process the optional arguments
    parser = argparse.ArgumentParser(parents=[parser])    
    for option in target_mimetype.options:
        parser.add_argument("--"+option.name, dest=option.name, default=option.default_value, help='%s (%s) [default: %s] (%s)'%(option.description, option.constraint, option.default_value, option.type))

    options = parser.parse_args()
    
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
