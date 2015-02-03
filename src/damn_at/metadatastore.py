"""
The MetaDataStore handler.
"""
import os
from .utilities import is_existing_file, pretty_print_file_description
from .bld import hash_to_dir

from damn_at.serialization import SerializeThriftMsg, DeserializeThriftMsg

from damn_at import FileDescription


class MetaDataStoreException(Exception):
    """Base MetaDataStore Exception"""
    def __init__(self, msg, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class MetaDataStoreFileException(MetaDataStoreException):
    """Something wrong with the file"""
    pass


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
        return is_existing_file(os.path.join(self.store_path, hash_to_dir(an_hash)))

    def get_metadata(self, store_id, an_hash):
        """
        Get the FileDescription for the given hash.
        """
        try:
            with open(os.path.join(self.store_path, hash_to_dir(an_hash)), 'rb') as metadata:
                a_file_descr = DeserializeThriftMsg(FileDescription(), metadata.read())
                return a_file_descr
        except IOError as ioe:
            raise MetaDataStoreFileException('Failed to open FileDescription with hash %s' % an_hash, ioe)

    def write_metadata(self, store_id, an_hash, a_file_descr):
        """
        Write the FileDescription to this store.
        """
        data = SerializeThriftMsg(a_file_descr)
        path = os.path.join(self.store_path, hash_to_dir(an_hash))
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, 'wb') as metadata:
            metadata.write(data)
        return a_file_descr
