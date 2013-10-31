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
    'install_requires': ['Yapsy', 'pylint'],
    'packages': ['damn_at'],
    'scripts': [],
    'name': 'damn_at'
}

setup(**config)
