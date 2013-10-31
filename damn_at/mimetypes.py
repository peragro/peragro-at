"""
Role
====

Replacement for system's mimetype, adding some new types
and cleaning up reverse map for cleaner file extensions.
"""

from __future__ import absolute_import
import mimetypes as sys_mimetypes
sys_mimetypes.add_type("application/x-blender", ".blend")
sys_mimetypes.add_type("image/tga", ".tga")
sys_mimetypes.add_type("application/x-crystalspace.library+xml", ".xml")
sys_mimetypes.add_type("image/x-dds", ".dds")

try:
    # Remove .jpe from mimetype extensions, cause it annoys people.
    sys_mimetypes._db.types_map_inv[True].get("image/jpeg", []).remove('.jpe')
    sys_mimetypes._db.types_map_inv[True].get("audio/ogg", []).remove('.oga')
except (ValueError, ImportError, ):
    pass

guess_type = sys_mimetypes.guess_type
