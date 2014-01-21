"""
The DAMN AT module.
"""
from __future__ import absolute_import
import sys
import logging
logger = logging.getLogger('damn_at') # pylint: disable=C0103

from metrology.registry import registry
#registry = Registry() # pylint: disable=C0103

from damn_at.serialization.generated.damn_types.ttypes import TargetMimetype, TargetMimetypeOption
from damn_at.serialization.generated.damn_types.ttypes import MetaDataType, MetaDataValue
from damn_at.serialization.generated.damn_types.ttypes import FileId, FileDescription
from damn_at.serialization.generated.damn_types.ttypes import AssetId, AssetDescription

from damn_at.analyzer import Analyzer
from damn_at.metadatastore import MetaDataStore


_CMD_DESCRIPTION = '''
 ___   _   __  __ _  _ 
|   \ /_\ |  \/  | \| |
| |) / _ \| |\/| | .` |
|___/_/ \_\_|  |_|_|\_|
    Digital Assets Managed Neatly.
'''
