"""
Generic Image analyzer.
"""
import os

import mimetypes

import subprocess

from damn_at import FileId, FileDescription, AssetDescription, AssetId

from damn_at.pluginmanager import IAnalyzer


class GenericImageAnalyzer(IAnalyzer):
    """Generic Image analyzer."""
    handled_types = ["image/x-ms-bmp", "image/jpeg", "image/png", "image/gif", "image/x-photoshop", "image/tiff"]
    
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

        try:
            pro = subprocess.Popen(['exiftool',an_uri], stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            out, err = pro.communicate()
            if pro.returncode != 0:
                print("E: ImageAnalyzer failed %s with error code %d! "
                        %(an_uri, pro.returncode), out, err)
                return False
        except OSError:
            print("E: ImageAnalyzer failed %s" %(an_uri), out, err)
            return False
            
        meta = {}
        lines = out.strip().split('\n')

        file_descr.assets.append(asset_descr) 
        
        return file_descr
