"""
"""
import os
from .pluginmanager import DAMNPluginManagerSingleton
from .utilities import is_existing_file

from .thrift.serialization import SerializeThriftMsg, DeserializeThriftMsg

from damn_at.thrift.generated.damn_types.ttypes import FileReference


class MetaDataStore(object):
    """
    """
    def __init__(self):
        plugin_mgr = DAMNPluginManagerSingleton.get()
        """
        for plugin in plugin_mgr.getPluginsOfCategory('MetaDataStore'):
            if plugin.plugin_object.is_activated:
                for mimetype in plugin.plugin_object.handled_types:
                    self.analyzers[mimetype] = plugin.plugin_object
        """
    
    def is_in_store(self, store_id, an_hash):
        """
        """
        return is_existing_file(os.path.join(store_id, an_hash))
        
    def get_metadata(self, store_id, an_hash):
        """
        """
        metadata = file(os.path.join(store_id, an_hash), 'rb')
        a_file_ref = DeserializeThriftMsg(FileReference(), metadata.read())
        metadata.close()
        return a_file_ref
        
    def write_metadata(self, store_id, an_hash, a_file_ref):
        """
        """
        data = SerializeThriftMsg(a_file_ref)
        metadata = file(os.path.join(store_id, an_hash), 'wb')
        metadata.write(data)
        metadata.close()
        return a_file_ref
