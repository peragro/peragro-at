import os
import re
import subprocess
from setuptools import setup
from setuptools import find_packages


def version():
    try:
        pkg_info_version_re = re.compile("\nVersion: ([^\s]*)\n")
        caller_path = os.path.dirname(__file__)
        fd = open(os.path.join(caller_path, 'PKG-INFO'))
        match = pkg_info_version_re.search(fd.read())
        if match:
            return match.groups()[0]
        else:
            raise Exception("No version match.")
    except Exception:
        args = ["git", "describe", "--all", "--always", "--dirty"]
        try:
            return subprocess.check_output(args).rstrip().lstrip("tags/")
        except Exception:
            return "0.0.0-development"

INSTALL_REQUIRES = ['Yapsy', 'Image', 'gitpython', 'ffvideo', 'filemagic',
                    'logilab-common']

setup(
    name='damn_at',
    description='Digital Assets Managed Neatly: Analyzers and Transcoders',
    packages=find_packages('src'),
    package_dir={"": "src"},
    version=version(),
    author='sueastside',
    url='https://github.com/sueastside/damn-at',
    download_url='https://github.com/sueastside/damn-at',
    author_email='No, thanks',
    test_suite="tests",
    install_requires=INSTALL_REQUIRES,
    scripts=[],
    entry_points={
        'console_scripts': ['pt = damn_at.cli:main',
                            'damn_at-server = damn_at.thrift.server:main',
                            'damn_at-analyze = damn_at.analyzer:main',
                            'damn_at-transcode = damn_at.transcoder:main',
                            'damn_fs = damn_at.damnfs.damnfs:main']
    }
)
