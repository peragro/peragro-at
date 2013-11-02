"""
General utilities.
"""
import os
import subprocess

def is_existing_file(an_uri):
    """Returns whether the file exists and it is an actual file. 
    :param an_uri: the URI pointing to the file to be analyzed
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
    paths = []
    dirname = os.path.dirname(__file__)
    paths.append(os.path.join(dirname, '..'))
    paths.append('/usr/local/lib/python3.2/dist-packages/thrift-0.9.1-py3.2.egg')
    env = dict(os.environ)
    env['PYTHONPATH'] = os.pathsep.join(paths)
    args = ['blender', "-b", an_uri, '-P', script_uri]

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode
