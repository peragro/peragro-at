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
    with open(an_uri, 'rb') as fh:
        while True:
            buf = fh.read(4096)
            if not buf : break
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
    stdout, stderr = process.communicate()
    for path in stdout.split('\n'):
        for include in glob.glob(path+'/*.egg'):
            paths.append(include)
        for include in glob.glob(path+'/*.egg-link'):
            with open(include, 'rb') as data:
                for include_path in data.read().split('\n'):
                    include_path = os.path.join(include, include_path)
                    paths.append(include_path)
                    
    return paths


def get_referenced_file_ids(file_ref):
    """Collect all FileIds in a FileReference"""
    file_ids = []
    def analyze_dependency(asset_id):
        file_ids.append(asset_id.file)
   
    def analyze_asset_ref(asset_ref):
        file_ids.append(asset_ref.asset.file)
        if asset_ref.dependencies:
            for dependency in asset_ref.dependencies:
                analyze_dependency(dependency)
                
    def analyze_file_ref(file_ref):
        file_ids.append(file_ref.file)
        if file_ref.assets:
            for asset in file_ref.assets:
                analyze_asset_ref(asset)
                
    analyze_file_ref(file_ref)
    return file_ids
    
def abspath(path, file_ref=None):
    if file_ref:
        path = os.path.normpath(os.path.join(os.path.dirname(file_ref.file.filename), path))
    return path
