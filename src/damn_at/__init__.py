"""
The DAMN AT module.
"""
from __future__ import absolute_import
import imp
import logging
logger = logging.getLogger('damn_at')  # pylint: disable=C0103

# Yapsy logs failed plugins as errors, but we don't like that.
logging.getLogger('yapsy')._error = logging.getLogger('yapsy').error
logging.getLogger('yapsy').error = logging.getLogger('yapsy').info


from damn_at.serialization.generated.damn_types.ttypes import (
    TargetMimetype,
    TargetMimetypeOption,
    MetaDataType,
    MetaDataValue,
    FileId,
    FileDescription,
    AssetId,
    AssetDescription
)


def load_module(name):
    """Load module using imp.find_module"""
    names = name.split(".")
    path = None
    for name in names:
        f, path, info = imp.find_module(name, path)
        path = [path]
    return imp.load_module(name, f, path[0], info)


Analyzer = load_module("damn_at.analyzer").Analyzer
MetaDataStore = load_module("damn_at.metadatastore").MetaDataStore
Transcoder = load_module("damn_at.transcoder").Transcoder

# from damn_at.analyzer import Analyzer  # pylint: disable=W0611
# from damn_at.metadatastore import MetaDataStore  # pylint: disable=W0611
# from damn_at.transcoder import Transcoder  # pylint: disable=W0611

_CMD_DESCRIPTION = r'''
 ___   _   __  __ _  _
|   \ /_\ |  \/  | \| |
| |) / _ \| |\/| | .` |
|___/_/ \_\_|  |_|_|\_|
    Digital Assets Managed Neatly.
'''

__all__ = ['TargetMimetype', 'TargetMimetypeOption', 'MetaDataType',
           'MetaDataValue', 'FileId', 'FileDescription', 'AssetId',
           'AssetDescription', 'Analyzer', 'MetaDataStore', 'Transcoder']
