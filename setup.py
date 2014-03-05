try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Digital Assets Managed Neatly: Analyzers and Transcoders',
    'author': 'sueastside',
    'url': 'https://github.com/sueastside/damn-at',
    'download_url': 'https://github.com/sueastside/damn-at',
    'author_email': 'No, thanks',
    'version': '0.1',
    'test_suite': 'tests.suite',
    'install_requires': ['Yapsy', 'Image', 'pylint', 'thrift', 'metrology', 'gitpython'],
    'test_requires': [],
    'packages': ['damn_at'],
    'scripts': [],
    'name': 'damn_at',
    'entry_points':{
          'console_scripts':['damn_at-server = damn_at.thrift.server:main',
                             'damn_at-analyze = damn_at.analyzer:main',
                             'damn_at-transcode = damn_at.transcoder:main',
                             'damn_at-inspect = damn_at.metadatastore:main',
                             'damn_fs = damn_at.damnfs.damnfs:main']
    }
}

setup(**config)
