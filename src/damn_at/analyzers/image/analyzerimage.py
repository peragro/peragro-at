"""
Generic Image analyzer.
"""
import os

from damn_at import mimetypes

import subprocess

from damn_at import MetaDataType, MetaDataValue
from damn_at import FileId, FileDescription, AssetDescription, AssetId

from damn_at.pluginmanager import IAnalyzer

from damn_at.analyzer import AnalyzerException

class GenericImageAnalyzer(IAnalyzer):
    """Generic Image analyzer."""
    handled_types = ["image/x-ms-bmp", "image/jpeg", "image/png", "image/gif",
                     "image/x-photoshop", "image/tiff", "application/x-xcf"]

    def __init__(self):
        super(GenericImageAnalyzer, self).__init__()

    def activate(self):
        pass

    def analyze(self, an_uri):
        fileid = FileId(filename = os.path.abspath(an_uri))
        file_descr = FileDescription(file = fileid)
        file_descr.assets = []

        image_mimetype = mimetypes.guess_type(an_uri)[0]

        asset_descr = AssetDescription(asset = AssetId(subname = 'main layer', mimetype = image_mimetype, file = fileid))

        try:
            pro = subprocess.Popen(['exiftool',an_uri], stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
            out, err = pro.communicate()
            if pro.returncode != 0:
                print("E: ImageAnalyzer failed %s with error code %d! "
                        %(an_uri, pro.returncode), out, err)
                raise AnalyzerException("ImageAnalyzer failed %s with error code %d! "%(an_uri, pro.returncode))
        except OSError as e:
            print("E: ImageAnalyzer failed %s (%s)" %(an_uri, e))
            raise e
        meta = {}
        flag = 0
        lines = str(out).strip().split('\n')
        for line in lines:
            line = line.split(':', 1)
            if len(line) == 1:
                line = line[0].split('=')
            line = [l.strip() for l in line]
            if line[0] == 'MIME Type' : flag = 1
            if flag == 1 and line[0] not in ['MIME Type', 'Image Size']:
                meta[line[0].lower().replace(' ','_')] = line[1]

        from damn_at.analyzers.image import metadata

        extractor_mapping = {'image/png' : metadata.MetaDataPNG,
                'image/jpeg' : metadata.MetaDataJPG,
                'image/x-ms-bmp' : metadata.MetaDataBMP,
                'image/x-photoshop' : metadata.MetaDataPSD,
                'application/x-xcf' : metadata.MetaDataXCF,}

        if image_mimetype in extractor_mapping:
            asset_descr.metadata = extractor_mapping[image_mimetype].extract(meta)
        else:
            asset_descr.metadata = {}

        for key, value in meta.items():
            if key not in asset_descr.metadata:
                asset_descr.metadata['exif-'+key] = MetaDataValue(type=MetaDataType.STRING, string_value = value)

        file_descr.assets.append(asset_descr)

        return file_descr
