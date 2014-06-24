"""Analyzer for Videos """
import os
import subprocess
import mimetypes

from damn_at import MetaDataType, MetaDataValue
from damn_at import FileId, FileDescription, AssetDescription, AssetId

from damn_at.pluginmanager import  IAnalyzer
from damn_at.analyzers.video import metadata

class GenericVideoAnalyzer(IAnalyzer):
    """Generic Video Analyzer"""
    handled_types = ["video/mp4", "video/x-msvideo"]

    def __init__(self):
        IAnalyzer.__init__(self)

    def activate(self):
        pass

    def analyze(self, an_uri):
        fileid = FileId(filename=os.path.abspath(an_uri))
        file_descr = FileDescription(file=fileid)
        file_descr.assets = [] 
        video_mimetype = mimetypes.guess_type(an_uri)[0]
        asset_descr = AssetDescription(asset=AssetId(subname=os.path.basename(an_uri), 
            mimetype=video_mimetype, file=fileid))

        try:
            pro = subprocess.Popen(['exiftool', an_uri], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            out, err = pro.communicate()
            if pro.returncode != 0:
                print("VideoAnalyzer failed %s with error code %d" 
                        %(an_uri, pro.returncode), out, err)
                return False
        except OSError:
            print("VideoAnalyzer failed %s" %(an_uri), out, err)
            return False

        meta = {}
        flag = False
        lines = out.strip().split('\n')
        for line in lines:
            line = line.split(':', 1)
            if len(line) == 1:
                line = line.split('=')
            line = [l.strip() for l in line]
            if line[0] == 'MIME Type': 
                flag = True
                continue
            if flag:
                meta[line[0].lower().replace(' ', '_')] = line[1]

        asset_descr.metadata = metadata.MetaDataExif.extract(meta)
        for key, value in meta.items():
            if key not in asset_descr.metadata:
                asset_descr.metadata['Exif-'+key] = MetaDataValue(
                        type=MetaDataType.STRING, string_value=value)

        file_descr.assets.append(asset_descr)

        return file_descr
