"""
General utilities.
"""

import os
import subprocess
import glob
import hashlib
import urllib

def calculate_hash_for_file(an_uri):
    """Returns a sha1 hexdigest for the given file.

    :param an_uri: the URI pointing to the file
    :rtype: string
    """
    try:
        chksum = hashlib.sha1()
        with open(an_uri, 'rb') as filehandle:
            while True:
                buf = filehandle.read(4096)
                if not buf: 
                    break
                chksum.update(buf)
        return chksum.hexdigest()
    except IOError as io_error:
        return 'NOT_FOUND(%s)'%an_uri


def is_existing_file(an_uri):
    """Returns whether the file exists and it is an actual file. 

    :param an_uri: the URI pointing to the file
    :rtype: bool
    """
    return os.path.exists(an_uri) and not os.path.isdir(an_uri)


def script_path(filename):
    """b-script-'+__file__+'.py 

    :param filename: __file__
    :rtype: string
    """
    dirname = os.path.dirname(filename)
    fnoext = os.path.splitext(os.path.basename(filename))[0]
    return os.path.join(dirname, 'b-script-'+fnoext+'.py')


def run_blender(an_uri, script_uri, arguments=[]):
    """Runs blender with the given file and script"""
    paths = collect_python3_paths()

    dirname = os.path.dirname(__file__)
    paths.append(os.path.join(dirname, '..'))
    
    paths.append(os.path.dirname(script_uri))

    env = dict(os.environ)
    env['PYTHONPATH'] = os.pathsep.join(paths)
    args = ['blender', "-b", an_uri, '-P', script_uri]
    args.extend(arguments)

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode


def collect_python3_paths():
    """Collect python3's 'dist-packages' paths to create PYTHONPATH with"""
    paths = []
    args = ['python3', "-c", 'import site; [print(x) for x in site.getsitepackages()]']
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, _ = process.communicate()
    for path in stdout.split('\n'):
        for include in glob.glob(path+'/*.egg'):
            paths.append(include)
        for include in glob.glob(path+'/*.egg-link'):
            with open(include, 'rb') as data:
                for include_path in data.read().split('\n'):
                    include_path = os.path.join(include, include_path)
                    paths.append(include_path)

    return paths


def get_referenced_file_ids(file_descr):
    """Collect all FileIds in a FileDescription"""
    file_ids = []
    def analyze_dependency(asset_id):
        """Fetch the fileIds of an asset"""
        file_ids.append(asset_id.file)

    def analyze_asset_descr(asset_descr):
        """Fetch the fileIds of an asset_descr and its dependencies"""
        file_ids.append(asset_descr.asset.file)
        if asset_descr.dependencies:
            for dependency in asset_descr.dependencies:
                analyze_dependency(dependency)

    def analyze_file_descr(file_descr):
        """Fetch the fileIds of a file_descr and its assets"""
        file_ids.append(file_descr.file)
        if file_descr.assets:
            for asset in file_descr.assets:
                analyze_asset_descr(asset)

    analyze_file_descr(file_descr)
    return file_ids


def abspath(path, file_descr=None):
    """Return an absolute path using the given FileDescription as reference."""
    if file_descr:
        path = os.path.normpath(os.path.join(os.path.dirname(file_descr.file.filename), path))
    else:
        path = os.path.normpath(os.path.abspath(path))
    return path

    
def get_metadatavalue_type(value):
    """Return the name of the type and the value of the MetaDataValue

    :param value: :py:class:`damn_at.MetaDataValue` 
    :rtype: tuple<string,string>
    """
    from damn_at import MetaDataType
    name = MetaDataType._VALUES_TO_NAMES[value.type]
    field = name.lower()+'_value'
    return name, str(getattr(value, field, None))


def pretty_print_metadatavalue(key, value, indent=0):
    """Pretty print a given MetaDataValue

    :param key: the name of the MetaDataValue
    :param value: :py:class:`damn_at.MetaDataValue` 
    :param indent: indentation level
    """
    whitespace = ' '*indent
    type, val = get_metadatavalue_type(value)
    print(whitespace+'* '+key+': '+val+' ('+type+')')
   

def pretty_print_asset_id(asset_id, indent=0):
    """Pretty print a given AssetId

    :param asset_id: :py:class:`damn_at.AssetId` 
    :param indent: indentation level
    """
    whitespace = ' '*indent
    print(whitespace+'* %s (%s)'%(asset_id.subname, asset_id.mimetype))
    pretty_print_file_id(asset_id.file, indent+2)
 
    
def pretty_print_asset_descr(asset_descr, indent=0):
    """Pretty print a given AssetDescription

    :param asset_id: :py:class:`damn_at.AssetDescription` 
    :param indent: indentation level
    """
    whitespace = ' '*indent
    #print(whitespace+''+str(asset_descr))
    pretty_print_asset_id(asset_descr.asset)
    if asset_descr.dependencies:
        print(whitespace+'  Dependencies (%d):'%len(asset_descr.dependencies))
        for dep in asset_descr.dependencies:
            pretty_print_asset_id(dep, indent+4)
    if asset_descr.metadata:
        print(whitespace+'  MetaData (%d):'%len(asset_descr.metadata))
        for key, value in asset_descr.metadata.items():
            pretty_print_metadatavalue(key, value, indent+4)

    
def pretty_print_file_id(file_id, indent=0):
    """Pretty print a given FileId

    :param asset_id: :py:class:`damn_at.FileId` 
    :param indent: indentation level
    """
    whitespace = ' '*indent
    print(whitespace+'hash: '+file_id.hash)
    print(whitespace+'filename: '+file_id.filename)
 

def pretty_print_file_description(file_descr):
    """Pretty print a given FileDescription

    :param asset_id: :py:class:`damn_at.FileDescription` 
    :param indent: indentation level
    """
    pretty_print_file_id(file_descr.file)
    print('%d Assets: '%len(file_descr.assets) if file_descr.assets else 0)
    print('='*80)
    if file_descr.assets:
        for asset in file_descr.assets:
            pretty_print_asset_descr(asset)
            print('-'*80)
    print('\n')


def find_asset_ids_in_file_descr(file_descr, asset_name):
    """Find an AssetId by name in the given FileDescription

    :param file_descr: :py:class:`damn_at.FileDescription` 
    :param asset_name: string the asset to look for
    :rtype: list of :py:class:`damn_at.AssetId` 
    """
    asset_ids = []
    if file_descr.assets:
        for asset in file_descr.assets:
            if asset.asset.subname == asset_name:
                asset_ids.append(asset.asset)
    return asset_ids


def get_asset_names_in_file_descr(file_descr):
    """Get all asset names in the given FileDescription

    :param file_descr: :py:class:`damn_at.FileDescription` 
    :rtype: list<string> of asset names contained 
    """
    if file_descr.assets:
        return [asset.asset.subname for asset in file_descr.assets]
    else:
        return []


def unique_asset_id_reference(asset_id):
    name = '%s%s%s' % (asset_id.file.hash, asset_id.subname, asset_id.mimetype)
    return urllib.quote(name.replace('/', '__'))
