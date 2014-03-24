"""
Generic Image analyzer.
"""
import os

import mimetypes

from damn_at import logger
from damn_at.analyzer import AnalyzerException
from damn_at import FileId, FileDescription, AssetDescription, AssetId

from damn_at.pluginmanager import IAnalyzer
from damn_at.utilities import script_path, run_blender

class GenericImageAnalyzer(IAnalyzer):
    """Generic Image analyzer."""
    handled_types = ["image/x-ms-bmp", "image/jpeg", "image/png"]
    
    def __init__(self):
        IAnalyzer.__init__(self)
      
    def activate(self):
        pass

    def analyze(self, an_uri):
    	fileid = FileId(filename = os.path.abspath(an_uri))
        file_descr = FileDescription(file = fileid)
        file_descr.assets = []
        
        image_mimetype = mimetypes.guess_type(an_uri)[0]
        
        asset_descr = AssetDescription(asset = AssetId(subname = os.path.basename(an_uri), mimetype = image_mimetype, file = fileid))
        file_descr.assets.append(asset_descr) 
        
        return file_descr
        
        














