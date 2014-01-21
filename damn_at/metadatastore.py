"""
The MetaDataStore handler.
"""
import os
from .utilities import is_existing_file, pretty_print_file_description

from damn_at.serialization import SerializeThriftMsg, DeserializeThriftMsg

from damn_at import FileDescription


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
        Get the FileDescription for the given hash.
        """
        with open(os.path.join(self.store_path, an_hash), 'rb') as metadata:
            a_file_descr = DeserializeThriftMsg(FileDescription(), metadata.read())
            return a_file_descr
        
    def write_metadata(self, store_id, an_hash, a_file_descr):
        """
        Write the FileDescription to this store.
        """
        data = SerializeThriftMsg(a_file_descr)
        with open(os.path.join(self.store_path, an_hash), 'wb') as metadata:
            metadata.write(data)
        return a_file_descr



def main():
    import sys
    from optparse import OptionParser
    import logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    
    file_path = sys.argv[1]

    m = MetaDataStore(os.path.dirname(file_path))
    
    from damn_at import _CMD_DESCRIPTION

    usage = "usage: %prog <file_path> [options] " + _CMD_DESCRIPTION
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args(sys.argv[1:])

    file_descr = m.get_metadata('', os.path.basename(file_path))
    print(_CMD_DESCRIPTION)
    print('Inspecting "%s"\n'%file_path)
    pretty_print_file_description(file_descr)
    
    
if __name__ == '__main__': 
    main()
