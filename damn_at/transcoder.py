"""
Role
====
Transcoder convience class to find the right plugin for a mimetype
and address it.
"""

from metrology.instruments.gauge import Gauge

from . import registry
from .pluginmanager import DAMNPluginManagerSingleton

from damn_at import TargetMimetype, TargetMimetypeOption
from .options import options_to_template


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
    
    def get_target_mimetypes(self):
        """Returns a list of supported mimetypes, 'handled_types' of all analyzers
        
        :rtype: map<string, list<TargetMimetype>>
        """
        target_mimetypes = {}
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
                    if not src_mimetype in target_mimetypes:
                        target_mimetypes[src_mimetype] = []
                    target_mimetypes[src_mimetype].append(tmt)
        return target_mimetypes


def main():
    import sys
    from optparse import OptionParser
    import logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    
    from damn_at.metadatastore import MetaDataStore
    
    store_path = sys.argv[1]
    file_name = sys.argv[2]
    mime_type = sys.argv[3]
    
    m = MetaDataStore(store_path)
    t = Transcoder()
    
    target_mimetypes = t.get_target_mimetypes()
    
    if mime_type not in target_mimetypes:
        raise TranscoderUnknownTypeException(mime_type+' needs to be one of '+str(target_mimetypes.keys()))
        
    target_mimetype = target_mimetypes[mime_type]

    usage = "usage: %prog <store_path> <file_path> <mime_type> [options] "
    parser = OptionParser(usage=usage)
    for option in target_mimetype[0].options:
        parser.add_option("--"+option.name, dest=option.name, default=option.default_value, help='%s (%s) [default: %s]'%(option.description, option.constraint, option.default_value))

    (options, args) = parser.parse_args(sys.argv[3:])
    print(options)
    
    
if __name__ == '__main__': 
    main()
    #damn_at-transcode /tmp/damn  path/myfile.png image/jpeg -h
