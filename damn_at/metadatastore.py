"""
The MetaDataStore handler.
"""
import os
from .utilities import is_existing_file

from damn_at.serialization import SerializeThriftMsg, DeserializeThriftMsg

from damn_at import FileReference


class MetaDataStore(object):
    """
    A filesystem MetaDataStore implementation.
    """
    def __init__(self, store_path):
        self.store_path = store_path
        if not os.path.exists(self.store_path):
            os.makedirs(self.store_path)

    def is_in_store(self, store_id, an_hash):
        """
        Check if the given file hash is in the store.
        """
        return is_existing_file(os.path.join(self.store_path, an_hash))
        
    def get_metadata(self, store_id, an_hash):
        """
        Get the FileReference for the given hash.
        """
        with open(os.path.join(self.store_path, an_hash), 'rb') as metadata:
            a_file_ref = DeserializeThriftMsg(FileReference(), metadata.read())
            return a_file_ref
        
    def write_metadata(self, store_id, an_hash, a_file_ref):
        """
        Write the FileReference to this store.
        """
        data = SerializeThriftMsg(a_file_ref)
        with open(os.path.join(self.store_path, an_hash), 'wb') as metadata:
            metadata.write(data)
        return a_file_ref
