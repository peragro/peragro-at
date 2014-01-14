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
        
        :rtype: list<string>
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

