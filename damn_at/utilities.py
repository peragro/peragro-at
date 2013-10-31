"""
General utilities.
"""
import os

def is_existing_file(an_uri):
    """Returns whether the file exists and it is an actual file. 
    arguments:
    anURI -- the URI pointing to the file to be analyzed
    """
    return os.path.exists(an_uri) and not os.path.isdir(an_uri)
