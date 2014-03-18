"""
The DAMN AT module.
"""
from __future__ import absolute_import
import logging
logger = logging.getLogger('damn_at') # pylint: disable=C0103

from metrology.registry import registry # pylint: disable=W0611
#registry = Registry() # pylint: disable=C0103

from damn_at.serialization.generated.damn_types.ttypes import TargetMimetype, TargetMimetypeOption # pylint: disable=W0611
from damn_at.serialization.generated.damn_types.ttypes import MetaDataType, MetaDataValue # pylint: disable=W0611
from damn_at.serialization.generated.damn_types.ttypes import FileId, FileDescription # pylint: disable=W0611
from damn_at.serialization.generated.damn_types.ttypes import AssetId, AssetDescription # pylint: disable=W0611

from damn_at.analyzer import Analyzer # pylint: disable=W0611
from damn_at.metadatastore import MetaDataStore # pylint: disable=W0611
from damn_at.transcoder import Transcoder # pylint: disable=W0611

_CMD_DESCRIPTION = r'''
 ___   _   __  __ _  _ 
|   \ /_\ |  \/  | \| |
| |) / _ \| |\/| | .` |
|___/_/ \_\_|  |_|_|\_|
    Digital Assets Managed Neatly.
'''
