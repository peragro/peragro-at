"""
PIL Image analyzer.
"""
# Standard
import os

# 3rd Party
from PIL import Image

# Damn
from damn_at import (
    mimetypes,
    FileId,
    FileDescription,
    AssetDescription,
    AssetId
)
from damn_at.pluginmanager import IAnalyzer


class GenericImageAnalyzer(IAnalyzer):
    """PIL Image analyzer."""
    handled_types = ["image/tga"]

    def __init__(self):
        super(GenericImageAnalyzer, self).__init__()

    def activate(self):
        pass

    def analyze(self, an_uri):
        fileid = FileId(filename=os.path.abspath(an_uri))
        file_descr = FileDescription(file=fileid)
        file_descr.assets = []

        image_mimetype = mimetypes.guess_type(an_uri)[0]

        asset_descr = AssetDescription(asset=AssetId(
            subname='main layer',
            mimetype=image_mimetype,
            file=fileid
        ))

        im = Image.open(an_uri)

        meta = {'format': im.format, 'size': im.size, 'mode': im.mode}
        meta.update(im.info)

        from damn_at.analyzers.image.metadata import MetaDataTGA

        asset_descr.metadata = MetaDataTGA.extract(meta)

        file_descr.assets.append(asset_descr)

        return file_descr
