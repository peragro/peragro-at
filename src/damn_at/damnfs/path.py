"""
Path utilities for DAMN FS
"""
import os

FILE_MARKER = '<children>'


def attach(file_id, trunk, branch=None):
    """Insert a branch of directories on its trunk."""
    if branch is None:
        branch = file_id.filename

    parts = branch.split('/', 1)
    if len(parts) == 1:  # branch is a file
        if file_id:
            found = False
            for _, fid in trunk[FILE_MARKER]:
                if fid.hash == file_id.hash:
                    found = True
                    break
            if not found:
                trunk[FILE_MARKER].append((parts[0], file_id))
    else:
        node, others = parts
        if node not in trunk:
            trunk[node] = {FILE_MARKER: []}
        attach(file_id, trunk[node], others)


def prettify(tree, indent=0):
    """Print the file tree structure with proper indentation."""
    for key, value in tree.iteritems():
        if key == FILE_MARKER:
            if value:
                print('  ' * indent + str(value))
        else:
            print('  ' * indent + str(key))
            if isinstance(value, dict):
                prettify(value, indent+1)
            else:
                print('  ' * (indent+1) + str(value))


def normdirpath(path):
    """Make a directory path end with /"""
    if not path.endswith('/') and path != '':
        path += '/'
    return path


def path_depth(path):
    """Give the depth, the number of directories deep, of a path"""
    parts = os.path.dirname(path).split('/')
    parts = [part for part in parts if part != '']
    length = len(parts)
    return length


def expand_path(path, start_path, base_depth):
    """Make a path relative to the given starting path and make the path
    atleast base_depth deep by prepending '_' directories.

    :param path: :py:class:`string`: the path to expand
    :param start_path: :py:class:`damn_at.FileDescription`: the starting path
    :param base_depth: :py:class:`int`: how deep the the base file should be
    :rtype: :py:class:`string`
    """
    path = path.replace(start_path, '')
    path = os.path.normpath(path)
    pathdepth = path_depth(path)
    path = path.replace('../', '', base_depth)
    if base_depth > pathdepth:
        for _ in range(base_depth - path_depth(path)):
            path = '_/' + path
    return path


def file_ids_as_tree(file_ids, start_path):
    """Create a tree like structure using the filenames of the given FileIds.

    :param file_ids: :py:func:`list` of :py:class:`damn_at.thrift.generated.damn_types.ttypes.FileId`
    :param start_path: :py:class:`string`: the base path
    :rtype: :py:class:`dict` {'adir':<>, '<files>':[...]}
    """
    relative_path = normdirpath(start_path)

    paths = {file_id.filename.replace(relative_path, '') for file_id in file_ids}
    base_depth = max([path.count('../') for path in paths])

    main_dict = {FILE_MARKER: []}
    for file_id in file_ids:
        attach(
            file_id,
            main_dict,
            expand_path(file_id.filename, relative_path, base_depth)
        )

    return main_dict


def get_files_for_path(file_ids_tree, path):
    """Traverse the FileIds tree with the given path and return the sub-tree
    at that level or the file if a leaf-node.

    :param file_ids_tree: :py:class:`dict` {'adir':<>, '<files>':[...]}
    :param path: :py:class:`string`: the path
    :rtype: :py:class:`dict` {'adir':<>, '<files>':[...]}
    """
    entry = file_ids_tree
    parts = path.split('/')
    for part in parts:
        if part != '':
            try:
                entry = entry[part]
            except KeyError as e:
                files = entry[FILE_MARKER]
                for entry in files:
                    if entry[0] == part:
                        return entry
                raise e

    return entry


def find_path_for_file_id(file_ids_tree, file_id):
    """Traverse the FileIds tree to construct a path for the given FileId

    :param file_ids_tree: :py:class:`dict` {'adir':<>, '<files>':[...]}
    :param file_id: :py:class:`damn_at.thrift.generated.damn_types.ttypes.FileId`: the fileId we're looking for
    :rtype: :py:class:`string`: the path
    """
    for key, value in file_ids_tree.iteritems():
        if key == FILE_MARKER:
            for name, fid in value:
                if fid.hash == file_id.hash:
                    return name
        else:
            if isinstance(value, dict):
                ret = find_path_for_file_id(value, file_id)
                if ret:
                    return key + '/' + ret


def parse_path(path):
    """Parse a path of /hash/action/my/path returning a tuple of
    ('hash', 'action', '/my/path') or None values if a shorter path is
    given.

    :param path: :py:class:`string`: the path
    :rtype: :py:func:`tuple`
    """
    if path == '/':
        return None, None, None
    paths = path[1:].split('/', 1)

    #Filter Empty strings
    paths = [p for p in paths if p != '']
    if len(paths) == 1:
        return paths[0], None, None
    else:
        file_hash, rest = paths
        paths = rest.split('/', 1)
        #Filter Empty strings
        paths = [p for p in paths if p != '']
        if len(paths) == 1:
            return file_hash, paths[0], None
        else:
            action, rest = paths
            return file_hash, action, rest
