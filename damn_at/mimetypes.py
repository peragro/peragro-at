"""
Role
====

Replacement for system's mimetype, adding some new types
and cleaning up reverse map for cleaner file extensions.
"""
import sys
import imp

#The following might conflict
#from __future__ import absolute_import
#import mimetypes as sys_mimetypes

#...so let's load it with some more magic.
search_paths = [path for path in sys.path[:] if path.find('damn_at') == -1]
file_handle, pathname, desc = imp.find_module('mimetypes', search_paths)
sys_mimetypes = imp.load_module('mimetypes', file_handle, pathname, desc)


sys_mimetypes.add_type("application/x-blender", ".blend")
sys_mimetypes.add_type("image/tga", ".tga")
sys_mimetypes.add_type("application/x-crystalspace.library+xml", ".xml")
sys_mimetypes.add_type("image/x-dds", ".dds")

#sys_mimetypes.add_type("image/jpg-reel", ".jpg")
#sys_mimetypes.add_type("image/png-reel", ".png")

try:
    # Remove .jpe from mimetype extensions, cause it annoys people.
    sys_mimetypes._db.types_map_inv[True].get("image/jpeg", []).remove('.jpe')
    sys_mimetypes._db.types_map_inv[True].get("audio/ogg", []).remove('.oga')
except (ValueError, ImportError, ):
    pass

guess_type = sys_mimetypes.guess_type

guess_extension = sys_mimetypes.guess_extension
