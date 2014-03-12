"""
Generic Image analyzer.
"""
import os

import mimetypes

from damn_at import FileId, FileDescription, AssetDescription, AssetId

from damn_at.pluginmanager import IAnalyzer

class GenericImageAnalyzer(IAnalyzer):
    """Generic Image analyzer."""
    handled_types = ["image/jpeg", "image/png"]
    
    def __init__(self):
        super(GenericImageAnalyzer, self).__init__()
      
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
        
        














