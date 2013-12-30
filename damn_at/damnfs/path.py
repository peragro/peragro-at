"""
Path utilities for DAMN FS
"""
import os


FILE_MARKER = '<children>'

def attach(file_id, trunk, branch=None):
    """
    Insert a branch of directories on its trunk.
    """
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


def prettify(d, indent=0):
    """
    Print the file tree structure with proper indentation.
    """
    for key, value in d.iteritems():
        if key == FILE_MARKER:
            if value:
                print '  ' * indent + str(value)
        else:
            print '  ' * indent + str(key)
            if isinstance(value, dict):
                prettify(value, indent+1)
            else:
                print '  ' * (indent+1) + str(value)


def normdirpath(path):
    """"""
    if not path.endswith('/') and path != '':
        path += '/'
    return path

 
def path_depth(path):
    """"""
    parts = os.path.dirname(path).split('/')
    parts = [part for part in parts if part != '']
    length = len(parts)
    return length

 
def expand_path(path, relative_path, base_depth):
    """"""
    path = path.replace(relative_path, '')
    path = os.path.normpath(path)
    path = path.replace('../', '_/', base_depth)
    if base_depth > path_depth(path):
        for x in range(base_depth - path_depth(path)):
           path = '_/' + path 
    return path

    
def file_ids_as_tree(file_ids, start_path):
    """"""
    relative_path = normdirpath(start_path)
    
    paths = set([file_id.filename.replace(relative_path, '') for file_id in file_ids])
    base_depth = max([path.count('../') for path in paths])
    #print(base_depth)
    
    main_dict = {FILE_MARKER: []}
    for file_id in file_ids:
        #print(expand_path(file_id.filename, relative_path, base_depth))
        attach(file_id, main_dict, expand_path(file_id.filename, relative_path, base_depth))
    
    return main_dict


def get_files_for_path(file_ids_tree, path):
    """"""
    entry = file_ids_tree
    parts = path.split('/')
    for part in parts:
        if part != '':
            try:
                entry = entry[part]
            except KeyError as e:
                print('get_files_for_path', e)
                files = entry[FILE_MARKER]
                for entry in files:
                    if entry[0] == part:
                        return entry
                
            
    return entry
