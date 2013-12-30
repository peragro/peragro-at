"""
Does some stuff
"""
import os
import unittest

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

from damn_at.thrift.generated.damn_types.ttypes import FileId

from damn_at.damnfs.path import file_ids_as_tree, prettify, get_files_for_path

class TestCase(unittest.TestCase):
    """Test case"""
    def test_file_ids_as_tree(self):
        """Test"""
        file_ids = []
        file_ids.append(FileId(filename='/home/sueastside/dev/DAMN/damn-test-files/mesh/blender/cube1.blend'))
        file_ids.append(FileId(filename='../../image/jpg/crate10b.jpg'))
        file_ids.append(FileId(filename='../../image/jpg/crate10.jpg'))
        
        main_dict = file_ids_as_tree(file_ids, '/home/sueastside/dev/DAMN/damn-test-files/mesh/blender')
        
        #prettify(main_dict)
        assert True
        
    def test_file_ids_at_path(self):
        """Test"""
        
        file_ids = []
        file_ids.append(FileId(hash='1', filename='test.blend'))
        file_ids.append(FileId(hash='2',filename='../../image/jpeg/test-image1.jpg'))
        file_ids.append(FileId(hash='3',filename='../../image/test-image2.image'))
        file_ids.append(FileId(hash='4',filename='../../image/jpeg/test-image3.jpg'))

        
        main_dict = file_ids_as_tree(file_ids, '')
        #prettify(main_dict)
        
        paths = [('', 0), ('_/', 0), ('_/_/', 1), ('_/_/image/', 1), ('_/_/image/jpeg', 2)]
        for path, count in paths:
            files = get_files_for_path(main_dict, path)
            #print('path', path, files['<children>'])
            assert len(files['<children>']) == count
        
        
        assert True

def test_suite():
    """Return a list of tests"""
    return unittest.TestLoader().loadTestsFromTestCase(TestCase)

if __name__ == '__main__':
    #unittest.main()
    unittest.TextTestRunner().run(test_suite())
