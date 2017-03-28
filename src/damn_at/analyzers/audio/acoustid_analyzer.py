'''Analyzer for audio files using AcoustID'''
from __future__ import print_function
import os
import mimetypes
import subprocess
import uuid
from damn_at import logger
from damn_at import AssetId, FileId, FileDescription, AssetDescription
from damn_at.pluginmanager import IAnalyzer
from damn_at.analyzers.audio import metadata

from acoustid import fingerprint_file


def get_supported_formats():
    try:
        pro = subprocess.Popen(['ffmpeg', '-formats'], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, err = pro.communicate()
        if pro.returncode != 0:
            logger.debug(
                "GetAcoustIDTypes failed with error code %d! " % (pro.returncode),
                out,
                err
            )
            return []
    except OSError as oserror:
        logger.debug("GetAcoustIDTypes failed! %s", oserror)
        return []

    extensions = [line.split()[1] for line in str(out).split("\n")[4:] if len(line.split()) > 1]
    mimes = []
    for ext in extensions:
        mime = mimetypes.guess_type('file.' + ext, False)[0]
        if mime and mime.startswith('audio/'):
            mimes.append(mime)
    return mimes


class SoundAnalyzer(IAnalyzer):
    '''Class for sound analyzer called in the analyzer'''

    handled_types = get_supported_formats()

    def __init__(self):
        IAnalyzer.__init__(self)

    def activate(self):
        pass

    def analyze(self, anURI):
        fileid = FileId(filename=os.path.abspath(anURI))
        file_descr = FileDescription(file=fileid)
        file_descr.assets = []

        asset_descr = AssetDescription(asset=AssetId(subname=os.path.basename(anURI),
                                       mimetype=mimetypes.guess_type(anURI, False)[0],
                                       file=fileid))

        try:
            duration, fingerprint = fingerprint_file(anURI)
            fingerprint_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, str(duration)+fingerprint)
        except Exception as e:
            print(("E: AcoustID analyzer failed %s with error %s" % (anURI, e)))
        meta = {'duration': str(duration)+'s', 'fingerprint': fingerprint, 'fingerprint_uuid': fingerprint_uuid}
        asset_descr.metadata = metadata.MetaDataAcoustID.extract(meta)
        file_descr.assets.append(asset_descr)

        return file_descr
