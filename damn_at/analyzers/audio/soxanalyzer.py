import os
import subprocess
import re
import mimetypes

from damn_at import AssetId, FileId, FileDescription, AssetDescription
from damn_at import MetaDataValue, MetaDataType
from damn_at.pluginmanager import IAnalyzer
#from damn.util import ExecutableDependencies

#ExecutableDependencies(['sox'])

def GetSoxTypes():
    try:
        p = subprocess.Popen(['sox', '-h'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        s, t = p.communicate()
        if p.returncode != 0:
            print("E: GetSoxTypes failed with error code %d! "%(p.returncode), s, t)
            return []
    except OSError:
        print("E: GetSoxTypes failed!", s, t)
        return []

    match = re.search(r'AUDIO FILE FORMATS:(.*)PLAYLIST FORMATS', s, re.DOTALL)
    if not match:
        print("E: GetSoxTypes failed to parse output!", s, t)
        return []

    extensions = match.group(1).strip().split(' ')
    mimes = []
    for ext in extensions:
        mime = mimetypes.guess_type('file.'+ext, False)[0]
        if mime: mimes.append(mime)
    return mimes

class SoundAnalyzer(IAnalyzer):
    handled_types = GetSoxTypes()
    def __init__(self):
        IAnalyzer.__init__(self)

    def activate(self):
        pass

    def analyze(self, anURI):
        fileId = FileId( filename = os.path.abspath(anURI) ) 
        f = FileDescription(file = fileId)
        f.assets = []

        asset_descr = AssetDescription( asset =
        AssetId(subname=os.path.basename(anURI), mimetype=mimetypes.guess_type(anURI, False)[0], file=fileId ) )

        try:
            p = subprocess.Popen(['sox', '--i', anURI], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            s, t = p.communicate()
            if p.returncode != 0:
                print("E: SoundAnalyzer failed %swith error code %d! "%(anURI, p.returncode), s, t)
                return False
        except OSError:
            print("E: SoundAnalyzer failed %s!"%(anURI), s, t)
            return False
        asset_descr.metadata = {}
        meta = {}
        lines = s.strip().split('\n')
        for line in lines:
            line = line.split(':', 1)
            if len(line) == 1:
                line = line[0].split('=')
            line = [l.strip() for l in line]
            if line[0] in ['Input File', 'Comment']: continue
            meta['Sox-'+line[0]] = line[1]
            asset_descr.metadata['Sox-'+line[0]] = MetaDataValue(type=MetaDataType.STRING, string_value = line[1])

        f.assets.append(asset_descr)

        return f
