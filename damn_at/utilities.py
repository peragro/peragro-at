"""
General utilities.
"""

import os
import subprocess
import glob
import hashlib

def calculate_hash_for_file(an_uri):
    """Returns a sha1 hexdigest for the given file.

    :param an_uri: the URI pointing to the file
    :rtype: string
    """
    chksum = hashlib.sha1()
    with open(an_uri, 'rb') as filehandle:
        while True:
            buf = filehandle.read(4096)
            if not buf: 
                break
            chksum.update(buf)
    return chksum.hexdigest()


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


def run_blender(an_uri, script_uri):
    """Runs blender with the given file and script"""
    paths = collect_python3_paths()

    dirname = os.path.dirname(__file__)
    paths.append(os.path.join(dirname, '..'))

    env = dict(os.environ)
    env['PYTHONPATH'] = os.pathsep.join(paths)
    args = ['blender', "-b", an_uri, '-P', script_uri]

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
