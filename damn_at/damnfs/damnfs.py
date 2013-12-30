#!/usr/bin/env python

'''
damn_at-analyze /home/sueastside/dev/DAMN/damn-test-files/mesh/blender/cube1.blend
damn_fs -f /tmp/damnfs/
'''

import os, sys
import time
from errno import *
from stat import *
import fcntl

import fuse
from fuse import Fuse

from damn_at.thrift.serialization import SerializeThriftMsg, DeserializeThriftMsg

from damn_at.thrift.generated.damn_types.ttypes import FileReference

from damn_at.utilities import get_referenced_file_ids

from damn_at.damnfs.path import file_ids_as_tree, get_files_for_path, FILE_MARKER


if not hasattr(fuse, '__version__'):
    raise RuntimeError, \
        "your fuse-py doesn't know of fuse.__version__, probably it's too old."

fuse.fuse_python_api = (0, 2)

# We use a custom file class
fuse.feature_assert('stateful_files', 'has_init')


def flag2mode(flags):
    md = {os.O_RDONLY: 'r', os.O_WRONLY: 'w', os.O_RDWR: 'w+'}
    m = md[flags & (os.O_RDONLY | os.O_WRONLY | os.O_RDWR)]

    if flags | os.O_APPEND:
        m = m.replace('w', 'a', 1)

    return m
    
_file_timestamp = int(time.time())  
class MyStat(fuse.Stat):  
  """ 
  Convenient class for Stat objects. 
  Set up the stat object with appropriate 
  values depending on constructor args. 
  """  
  def __init__(self, is_dir, size):  
    fuse.Stat.__init__(self)  
    if is_dir:  
      self.st_mode = S_IFDIR | 0555  
      self.st_nlink = 2  
    else:  
      self.st_mode = S_IFREG | 0444  
      self.st_nlink = 1  
      self.st_size = size  
    self.st_atime = _file_timestamp  
    self.st_mtime = _file_timestamp  
    self.st_ctime = _file_timestamp  
    
def get_file_hash(path):
    paths = path[1:].split('/',1)
    if len(paths) == 1:
        return paths[0], None
    else:
        file_hash, rest = paths
        return file_hash, rest


class DamnFS(Fuse):

    def __init__(self, *args, **kw):
        Fuse.__init__(self, *args, **kw)
        self.root = '/tmp/damn'

    def fsinit(self):
        os.chdir('/tmp/damn')

    def getattr(self, path):
        print '*** getattr', path
        if path=='/':
            return MyStat(True, 0)
        else:
            file_hash, rest = get_file_hash(path)
            #print('file_hash', file_hash)
            metadata = file(os.path.join('/tmp/damn', file_hash), 'rb')
            a_file_ref = DeserializeThriftMsg(FileReference(), metadata.read())
            metadata.close()

            #print('rest', rest)
            if not rest:
                rest = ''
                
            file_ids = get_referenced_file_ids(a_file_ref)     
            file_id_paths = set([file_id.filename for file_id in file_ids])  
            tree = file_ids_as_tree(file_ids, os.path.dirname(a_file_ref.file.filename))
            files = get_files_for_path(tree, rest)
            print('files1', files)
            if isinstance(files, dict):
                return MyStat(True, 0)
            else:
                print('file', files)
                return MyStat(False, 4)

            
    def readdir(self, path, offset):
        print('***readdir', path) 
        #if path.startswith('/'):
        #    path = path[1:]   
        if path=='/':
            path = os.path.join('/tmp/damn', '')
            for e in os.listdir(path):
                yield fuse.Direntry(e)
        else:
            file_hash, rest = get_file_hash(path)
            #print('file_hash', file_hash)
            metadata = file(os.path.join('/tmp/damn', file_hash), 'rb')
            a_file_ref = DeserializeThriftMsg(FileReference(), metadata.read())
            metadata.close()

            print('rest', rest)
            if not rest:
                rest = ''
                
            file_ids = get_referenced_file_ids(a_file_ref)     
            file_id_paths = set([file_id.filename for file_id in file_ids])  
            print(os.path.dirname(a_file_ref.file.filename))
            print(file_id_paths)
            tree = file_ids_as_tree(file_ids, os.path.dirname(a_file_ref.file.filename))
            files = get_files_for_path(tree, rest)
            print('files', files)
            for key, value in files.iteritems():
                if key == FILE_MARKER:
                    for entry in value:
                        yield fuse.Direntry(entry[0])
                else:
                     yield fuse.Direntry(key)
    
    def utime ( self, path, times ):
        print '*** utime', path, times
        return -errno.ENOSYS

    
from threading import Thread
import time
import subprocess
def unmount(path):
    """Unmount the given mount point.

    This function shells out to the 'fusermount' program to unmount a
    FUSE filesystem.  It works, but it would probably be better to use the
    'unmount' method on the MountProcess class if you have it.
    """
    for num_tries in xrange(3):
        p = subprocess.Popen(["fusermount","-u",path],stderr=subprocess.PIPE)
        (stdout,stderr) = p.communicate()
        if p.returncode == 0:
            return
        if "not mounted" in stderr:
            return
        if "not found" in stderr:
            return
    raise OSError("filesystem could not be unmounted: %s (%s) " % (path, str(stderr).rstrip(),))

def main():
    server = DamnFS(version="%prog " + fuse.__version__,
                 usage=Fuse.fusage)

    server.parse(values=server, errex=1)

    #server.main()
    
    t = Thread(target=server.main)
    t.start()
    try:
        while True:
            time.sleep(20)
            print('loop')
    except KeyboardInterrupt:
        print('exitting')
        unmount('/tmp/damnfs')
        #t.join()


if __name__ == '__main__':
    main()
