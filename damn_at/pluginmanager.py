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
    """Interface class for an Analyzer"""

    handled_types = []
    """
    The mimetypes this analyzer can handle.
    Example::
    handled_types = ["application/x-blender"]
    """

    def analyze(self, an_uri):
        """Returns a FileDescription

        :param an_uri: the URI pointing to the file to be analyzed
        :rtype: :py:class:`damn_at.FileDescription`
        :raises: :py:class:`damn_at.analyzer.AnalyzerException`
        """
        raise NotImplementedError("'analyze' must be reimplemented by %s" % self)


class ITranscoder(IPlugin):
    """Interface class for a Transcoder"""

    convert_map = {}
    """
    The mimetypes this transocder can handle.
    Example::
    convert_map = {"image/tiff" : {"image/jpeg": [IntVectorOption(name='size', description='The target size of the image', size=2, default=(-1,-1))],
                                   "image/png": []
                                   }, }
    """

    def transcode(self, dest_path, file_descr, asset_id, target_mimetype, **options):
        """ blah """
        raise NotImplementedError("'transcode' must be reimplemented by %s" % self)


class IMetaDataStore(IPlugin):
    """Interface class for a MetaDataStore"""
    def is_in_store(self, store_id, an_hash):
        """
        Check if the given file hash is in the store.
        """
        raise NotImplementedError("'is_in_store' must be reimplemented by %s" % self)

    def get_metadata(self, store_id, an_hash):
        """
        Get the FileDescription for the given hash.
        """
        raise NotImplementedError("'get_metadata' must be reimplemented by %s" % self)

    def write_metadata(self, store_id, an_hash, a_file_descr):
        """
        Write the FileDescription to this store.
        """
        raise NotImplementedError("'write_metadata' must be reimplemented by %s" % self)


class IRepository(IPlugin):
    """Interface class for a Repository"""
    def get_meta_data(self, an_uri, a_file_descr):
        """
        """
        raise NotImplementedError("'get_meta_data' must be reimplemented by %s" % self)


class DAMNPluginManager(PluginManager):
    """Loads all analyzers and transcoders."""
    def __init__(self):
        directory = os.path.dirname(os.path.abspath(__file__))
        PluginManager.__init__(
            self,
            directories_list=[os.path.join(directory, 'analyzers'), os.path.join(directory, 'transcoders'), os.path.join(directory, 'repositories')],
            categories_filter={
                "Analyzer": IAnalyzer,
                "Transcoder": ITranscoder,
                "MetaDataStore": IMetaDataStore,
                "Repository": IRepository,
            },
            plugin_info_ext=('analyzer', 'transcoder', 'repository',)
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
                        raise ActivationFailedException('Failed to activate %s' % (plugin_info_reference.name))
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
