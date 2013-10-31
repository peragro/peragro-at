"""
Role
====

The ''DAMNPluginManager'' loads all analyzers and transcoders.

Don't use it directly, use ''DAMNPluginManagerSingleton'' instead.
"""
import os
import sys

from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManager

from . import logger

class ActivationFailedException(Exception):
    """ Plugin activation failed exception """
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return repr(self.msg)


class IAnalyzer(IPlugin):
    """Base class for an Analyzer""" 
    def analyze(self, an_uri):
        """Returns a list of AssetReference
        arguments:
        anURI -- the URI pointing to the file to be analyzed
        """
        raise NotImplementedError("'isValidPlugin' must be reimplemented by %s" % self)        


class ITranscoder(IPlugin):
    """Base class for an Transcoder"""
    def analyze(self, an_uri):
        """ blah """
        raise NotImplementedError("'isValidPlugin' must be reimplemented by %s" % self)        


class DAMNPluginManager(PluginManager):
    """Loads all analyzers and transcoders."""
    def __init__(self):
        directory = os.path.dirname(os.path.abspath(__file__))
        PluginManager.__init__(self, 
            directories_list=[os.path.join(directory, 'analyzers'), os.path.join(directory, 'transcoders')],
            categories_filter={
           "Analyzer" : IAnalyzer,
           "Transcoder" : ITranscoder,
           },
           plugin_info_ext=('analyzer', 'transcoder', )
        )
        
    def collect_plugins(self):
        """
        Walk through the plugins' places and look for plugins. Then
        for each plugin candidate look for its category, load it and
        stores it in the appropriate slot of the category_mapping.
        """              
        self.locatePlugins()
        all_plugins = self.loadPlugins()
   
        # Collect plugins with an error in the 'Failed'-category
        self.category_mapping["Failed"] = []
        for plugin_info_reference in all_plugins:
            if plugin_info_reference.error:
                self.category_mapping["Failed"].append(plugin_info_reference)
        
        # Activate all plugins
        for plugin_info_reference in self.getAllPlugins():
            plugin_to_activate = plugin_info_reference.plugin_object
            if plugin_to_activate is not None:
                try:
                    plugin_to_activate.activate()
                    plugin_to_activate.is_activated = True
                except Exception:
                    try:
                        raise ActivationFailedException('Failed to activate %s'%(plugin_info_reference.name))
                    except ActivationFailedException:
                        exc_info = sys.exc_info()
                        logger.error("Unable to activate plugin: %s" % plugin_info_reference.name, exc_info=exc_info)
                        plugin_info_reference.error = exc_info
                        self.category_mapping["Failed"].append(plugin_info_reference)


class DAMNPluginManagerSingleton(object):
    """
    Singleton version of the DAMNPluginManager.

    Being a singleton, this class should not be initialised explicitly
    and the ``get`` classmethod must be called instead.

    To call one of this class's methods you have to use the ``get``
    method in the following way:
    ``DAMNPluginManagerSingleton.get().themethodname(theargs)``
    """
    
    __instance = None
    
    __decoration_chain = None

    def __init__(self):
        """
        Initialisation: this class should not be initialised
        explicitly and the ``get`` classmethod must be called instead.
        """
        if self.__instance is not None:
            raise Exception("Singleton can't be created twice !")
                            
    def get(cls):
        """
        Actually create an instance
        """
        if cls.__instance is None:
            # initialise the 'inner' PluginManagerDecorator
            cls.__instance = DAMNPluginManager()        
            cls.__instance.collect_plugins()                
            logger.debug("PluginManagerSingleton initialised")
        return cls.__instance
    get = classmethod(get)

