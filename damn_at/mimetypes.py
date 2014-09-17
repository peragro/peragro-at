"""
Role
====

Replacement for system's mimetype, adding some new types
and cleaning up reverse map for cleaner file extensions.
"""
import os
import sys
import imp
import magic

#The following might conflict
#from __future__ import absolute_import
#import mimetypes as sys_mimetypes

#...so let's load it with some more magic.
search_paths = [path for path in sys.path[:] if path.find('damn_at') == -1]
file_handle, pathname, desc = imp.find_module('mimetypes', search_paths)
sys_mimetypes = imp.load_module('mimetypes', file_handle, pathname, desc)

# Add mimetypes that don't seem to be present by default
sys_mimetypes.add_type("application/x-blender", ".blend")
sys_mimetypes.add_type("image/tga", ".tga")
sys_mimetypes.add_type("application/x-crystalspace.library+xml", ".xml")
sys_mimetypes.add_type("image/x-dds", ".dds")

# Add special purpose meta-mimetypes for transcoding, only add them 
# to the inverse lookup table (mimetype->extension) and not to the
# (extension->mimetype) so they're never returned for extension lookups! 
sys_mimetypes._db.types_map_inv[True]["image/jpg-reel"] = [".jpg"]
sys_mimetypes._db.types_map_inv[True]["image/png-reel"] = [".png"]


try:
    # Remove .jpe from mimetype extensions, cause it annoys people.
    sys_mimetypes._db.types_map_inv[True].get("image/jpeg", []).remove('.jpe')
    sys_mimetypes._db.types_map_inv[True].get("audio/ogg", []).remove('.oga')
except (ValueError, ImportError, ):
    pass



guess_extension = sys_mimetypes.guess_extension

#guess_type = sys_mimetypes.guess_type
def guess_type(url, strict=True):
    """ Try to guess the mimetype for the given file using the 
    standard python mimetypes module. 
    If this fails fallback to libmagic.
    """
    res = sys_mimetypes.guess_type(url, strict)
    if res[0] is None:
        paths = [None]*2
    paths[0] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'magic.blender')
    paths[1] = '/usr/share/misc/magic.mgc'
    with magic.Magic(paths=paths, flags=magic.MAGIC_COMPRESS|magic.MAGIC_MIME_TYPE) as mm:
        return (mm.id_filename(url), None)
    return res
