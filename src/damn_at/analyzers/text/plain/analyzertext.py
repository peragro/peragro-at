"""
Generic Text analyzer.
"""
import os
import magic

from damn_at import (
    mimetypes,
    MetaDataType,
    MetaDataValue,
    FileId,
    FileDescription,
    AssetDescription,
    AssetId
)

from damn_at.pluginmanager import IAnalyzer


class GenericTextAnalyzer(IAnalyzer):
    """Generic Text analyzer."""
    handled_types = ["text/plain", ]

    def __init__(self):
        super(GenericTextAnalyzer, self).__init__()

    def activate(self):
        pass

    def analyze(self, an_uri):
        fileid = FileId(filename=os.path.abspath(an_uri))
        file_descr = FileDescription(file=fileid)
        file_descr.assets = []

        text_mimetype = mimetypes.guess_type(an_uri)[0]

        asset_descr = AssetDescription(asset=AssetId(
            subname='content',
            mimetype=text_mimetype,
            file=fileid
        ))

        num_lines = sum(1 for line in open(an_uri))

        with magic.Magic(flags=magic.MAGIC_MIME_ENCODING) as mm:
            charset = mm.id_filename(an_uri)

        asset_descr.metadata = {}

        asset_descr.metadata['lines'] = MetaDataValue(
            type=MetaDataType.INT,
            int_value=num_lines
        )
        asset_descr.metadata['charset'] = MetaDataValue(
            type=MetaDataType.STRING,
            string_value=charset
        )

        file_descr.assets.append(asset_descr)

        return file_descr
