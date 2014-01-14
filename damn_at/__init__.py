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
from damn_at.serialization.generated.damn_types.ttypes import FileId, FileReference
from damn_at.serialization.generated.damn_types.ttypes import AssetId, AssetReference

from damn_at.analyzer import Analyzer
from damn_at.metadatastore import MetaDataStore


