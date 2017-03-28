#!/usr/bin/env python

'''
mkdir /tmp/damn
mkdir /tmp/damnfs
damn_at-analyze /tmp/damn /home/sueastside/dev/DAMN/damn-test-files/
damn_fs -f /tmp/damnfs/
'''
# Standard
from __future__ import absolute_import
from __future__ import print_function
import os
import time
import stat
import logging
import subprocess
from threading import Thread

# 3rd Party
import fuse
from fuse import Fuse

# Damn
from damn_at.serialization import DeserializeThriftMsg
from damn_at import FileDescription
from damn_at.utilities import (
    get_referenced_file_ids,
    abspath
)
from damn_at.damnfs.path import (
    file_ids_as_tree,
    get_files_for_path,
    FILE_MARKER,
    parse_path,
    find_path_for_file_id
)
import six
from io import open

LOG = logging.getLogger(__name__)


if not hasattr(fuse, '__version__'):
    raise RuntimeError("your fuse-py doesn't know of fuse.__version__, "
                       "probably it's too old.")

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
        if os.name == 'nt':
            #windows doesnt support this stuff :(
            print("windows os doesnt support everything...")
        else:
            if is_dir:
                    print((os.name))
                    self.st_mode = stat.S_IFDIR | 0o555
                    self.st_nlink = 2
            else:
                self.st_mode = stat.S_IFREG | 0o444
                self.st_nlink = 1
                self.st_size = size
        self.st_atime = _file_timestamp
        self.st_mtime = _file_timestamp
        self.st_ctime = _file_timestamp


def get_file_descr(file_hash):
    path = os.path.join('/tmp/damn', file_hash)
    with open(path, 'rb') as metadata:
        file_descr = DeserializeThriftMsg(FileDescription(), metadata.read())
        return file_descr


class DamnFS(Fuse):

    def __init__(self, *args, **kw):
        Fuse.__init__(self, *args, **kw)
        self.root = '/tmp/damn'
        self.file_class = self.DAMNFile

    def fsinit(self):
        os.chdir('/tmp/damn')

    def getattr(self, path):
        file_hash, action, rest = parse_path(path)
        if file_hash is None:
            return MyStat(True, 0)
        else:
            if action is None:
                return MyStat(True, 0)
            elif action == 'mount':
                return self.getattr_mount(path, file_hash, action, rest)
            elif action == 'assets':
                return MyStat(True, 0)
                #return self.getattr_assets(path, file_hash, action, rest)

        LOG.debug('oops:\n\t%s\n\t%s\n\t%s' % (path, file_hash, action))

    def getattr_mount(self, path, file_hash, action, rest):
        file_descr = get_file_descr(file_hash)

        if not rest:
            rest = ''

        file_ids = get_referenced_file_ids(file_descr)
        tree = file_ids_as_tree(
            file_ids,
            os.path.dirname(file_descr.file.filename)
        )

        if rest == os.path.basename(file_descr.file.filename):
            path_to = find_path_for_file_id(tree, file_descr.file)
            LOG.debug("Rest:\n\t%s\n\t%s" % (rest, path_to))
            file_stat = self.getattr_mount_file(
                path,
                file_hash,
                action,
                rest,
                ('', file_descr.file),
                file_descr
            )
            if path_to.count('/') != 0:
                file_stat.st_mode = stat.S_IFLNK | 0o755
            return file_stat

        files = get_files_for_path(tree, rest)
        if isinstance(files, dict):
            return MyStat(True, 0)
        else:
            return self.getattr_mount_file(
                path,
                file_hash,
                action,
                rest,
                files,
                file_descr
            )

    def getattr_mount_file(self, path, file_hash,
                           action, rest, files, file_descr):
        abs_path = abspath(files[1].filename, file_descr)
        size = os.stat(abs_path).st_size if os.path.isfile(abs_path) else 0
        return MyStat(False, size)

    def readlink(self, path):
        LOG.debug("*** readlink: %s", path)
        file_hash, action, rest = parse_path(path)
        file_descr = get_file_descr(file_hash)

        file_ids = get_referenced_file_ids(file_descr)
        tree = file_ids_as_tree(
            file_ids,
            os.path.dirname(file_descr.file.filename)
        )

        path_to = find_path_for_file_id(tree, file_descr.file)

        return path_to

    def readdir(self, path, offset):
        file_hash, action, rest = parse_path(path)

        if file_hash is None:
            path = os.path.join('/tmp/damn', '')
            for e in os.listdir(path):
                yield fuse.Direntry(e)
        else:
            if action is None:
                for action in ['mount', 'assets']:
                    yield fuse.Direntry(action)
            elif action == 'mount':

                for entry in self.readdir_mount(path, offset, file_hash, action, rest):
                    yield entry
            elif action == 'assets':
                for entry in self.readdir_assets(path, offset, file_hash, action, rest):
                    yield entry

    def readdir_mount(self, path, offset, file_hash, action, rest):
        file_descr = get_file_descr(file_hash)

        LOG.debug('Rest:\n\t%s' % rest)
        if not rest:
            rest = ''

        if rest == '':
            yield fuse.Direntry(os.path.basename(file_descr.file.filename))

        file_ids = get_referenced_file_ids(file_descr)
        file_id_paths = {file_id.filename for file_id in file_ids}
        LOG.debug(os.path.dirname(file_descr.file.filename))
        LOG.debug(file_id_paths)
        tree = file_ids_as_tree(
            file_ids,
            os.path.dirname(file_descr.file.filename)
        )
        files = get_files_for_path(tree, rest)
        LOG.debug('Files:\n\t%s' % files)
        for key, value in six.iteritems(files):
            if key == FILE_MARKER:
                for entry in value:
                    yield fuse.Direntry(entry[0])
            else:
                yield fuse.Direntry(key)

    def readdir_assets(self, path, offset, file_hash, action, rest):
        file_descr = get_file_descr(file_hash)
        if rest is None:
            for asset_descr in file_descr.assets:
                asset_id = asset_descr.asset
                mimetype = str(asset_id.mimetype).replace('/', '!')
                yield fuse.Direntry(asset_id.subname+' ('+str(mimetype)+')')

    class DAMNFile(object):
        def __init__(self, path, flags, *mode):
            file_hash, action, rest = parse_path(path)

            file_descr = get_file_descr(file_hash)

            if not rest:
                rest = ''

            file_ids = get_referenced_file_ids(file_descr)
            tree = file_ids_as_tree(
                file_ids,
                os.path.dirname(file_descr.file.filename)
            )
            files = get_files_for_path(tree, rest)
            if not isinstance(files, dict):
                abs_path = abspath(files[1].filename, file_descr)

                self.file = os.fdopen(
                    os.open(abs_path, flags, *mode),
                    flag2mode(flags)
                )
                self.fd = self.file.fileno()

        def read(self, length, offset):
            self.file.seek(offset)
            return self.file.read(length)

        def release(self, flags):
            self.file.close()


def unmount(path):
    """Unmount the given mount point.

    This function shells out to the 'fusermount' program to unmount a
    FUSE filesystem.  It works, but it would probably be better to use the
    'unmount' method on the MountProcess class if you have it.
    """
    for num_tries in xrange(3):
        process = subprocess.Popen(
            ["fusermount", "-u", path],
            stderr=subprocess.PIPE
        )
        (stdout, stderr) = process.communicate()
        if process.returncode == 0:
            return
        if "not mounted" in stderr:
            return
        if "not found" in stderr:
            return
    raise OSError("filesystem could not be unmounted: %s (%s) " % (
        path,
        str(stderr).rstrip()
    ))


def main():
    server = DamnFS(version="%prog " + fuse.__version__,
                    usage=Fuse.fusage)

    server.parse(values=server, errex=1)

    #server.main()
    thread = Thread(target=server.main)
    thread.start()
    try:
        while True:
            time.sleep(20)
            LOG.debug('Loop...')
    except KeyboardInterrupt:
        LOG.info('Exitting')
        unmount('/tmp/damnfs')


if __name__ == '__main__':
    main()
