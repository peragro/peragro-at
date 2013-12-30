"""
Does some stuff
"""
import os
import unittest

import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

from damn_at.thrift.generated.damn_types.ttypes import FileId

from damn_at.damnfs.path import file_ids_as_tree, prettify, get_files_for_path, parse_path, find_path_for_file_id

class TestCase(unittest.TestCase):
    """Test case"""
    def test_file_ids_as_tree(self):
        """Test"""
        file_ids = []
        file_ids.append(FileId(filename='/home/sueastside/dev/DAMN/damn-test-files/mesh/blender/cube1.blend'))
        file_ids.append(FileId(filename='../../image/jpg/crate10b.jpg'))
        file_ids.append(FileId(filename='../../image/jpg/crate10.jpg'))
        
        main_dict = file_ids_as_tree(file_ids, '/home/sueastside/dev/DAMN/damn-test-files/mesh/blender')
        
        prettify(main_dict)
        assert True
        
    def test_file_ids_as_tree(self):
        """Test"""
        file_ids = []
        file_ids.append(FileId(hash='1', filename='/home/sueastside/dev/DAMN/damn-test-files/mesh/blender/cube1.blend'))
        file_ids.append(FileId(hash='2', filename='../../image/jpg/crate10b.jpg'))
        file_ids.append(FileId(hash='3', filename='../../image/jpg/crate10.jpg'))
        
        main_dict = file_ids_as_tree(file_ids, '/home/sueastside/dev/DAMN/damn-test-files/mesh/blender')
        
        prettify(main_dict)
        
        assert '_/_/cube1.blend' == find_path_for_file_id(main_dict, file_ids[0])
        assert 'image/jpg/crate10b.jpg' == find_path_for_file_id(main_dict, file_ids[1])
        assert 'image/jpg/crate10.jpg' == find_path_for_file_id(main_dict, file_ids[2])
        
    def test_file_ids_at_path(self):
        """Test"""
        
        file_ids = []
        file_ids.append(FileId(hash='1', filename='test.blend'))
        file_ids.append(FileId(hash='2',filename='../../image/jpeg/test-image1.jpg'))
        file_ids.append(FileId(hash='3',filename='../../image/test-image2.image'))
        file_ids.append(FileId(hash='4',filename='../../image/jpeg/test-image3.jpg'))

        
        main_dict = file_ids_as_tree(file_ids, '')
        prettify(main_dict)
        
        paths = [('', 0), ('_/', 0), ('_/_/', 1), ('image/', 1), ('image/jpeg', 2)]
        for path, count in paths:
            files = get_files_for_path(main_dict, path)
            #print('path', count, path, files.get('<children>', None), isinstance(files, dict))
            if isinstance(files, dict):
                assert len(files['<children>']) == count
            else:
                assert count == 1
        
        assert True
        
    def test_parse_path(self):
        """Test"""
        assert (None, None, None) == parse_path('/')
        
        assert ('file_hash', 'action', 'path') == parse_path('/file_hash/action/path')
        
        assert ('file_hash', 'action', None) == parse_path('/file_hash/action/')

        assert ('file_hash', 'action', None) == parse_path('/file_hash/action')

        assert ('file_hash', None, None) == parse_path('/file_hash/')

        assert ('file_hash', None, None) == parse_path('/file_hash')
        

def test_suite():
    """Return a list of tests"""
    return unittest.TestLoader().loadTestsFromTestCase(TestCase)

if __name__ == '__main__':
    #unittest.main()
    unittest.TextTestRunner().run(test_suite())
