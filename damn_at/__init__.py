"""
The DAMN AT module.
"""
import logging
logger = logging.getLogger('damn_at') # pylint: disable=C0103

from metrology.registry import registry
#registry = Registry() # pylint: disable=C0103

from .analyzer import Analyzer
from .metadatastore import MetaDataStore

from damn_at.thrift.generated.damn_types.ttypes import FileId, FileReference, AssetReference, MetaDataType
