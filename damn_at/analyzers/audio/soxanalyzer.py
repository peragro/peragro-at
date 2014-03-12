'''Analyzer for audio files using sox'''
import os
import subprocess
import re
import mimetypes

from damn_at import AssetId, FileId, FileDescription, AssetDescription
from damn_at import MetaDataValue, MetaDataType
from damn_at.pluginmanager import IAnalyzer
#from damn.util import ExecutableDependencies

#ExecutableDependencies(['sox'])

def get_sox_types():
    '''Extract all possible formats for the audio file and store their mime
    types'''
    try:
        pro = subprocess.Popen(['sox', '-h'], stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
        out, err = pro.communicate()
        if pro.returncode != 0:
            print("E: GetSoxTypes failed with error code %d! "%(pro.returncode),
                    out, err)
            return []
    except OSError:
        print("E: GetSoxTypes failed!", out, err)
        return []

    match = re.search(r'AUDIO FILE FORMATS:(.*)PLAYLIST FORMATS',
            out, re.DOTALL)
    if not match:
        print("E: GetSoxTypes failed to parse output!", out, err)
        return []

    extensions = match.group(1).strip().split(' ')
    mimes = []
    for ext in extensions:
        mime = mimetypes.guess_type('file.'+ext, False)[0]
        if mime: mimes.append(mime)
    return mimes

class SoundAnalyzer(IAnalyzer):
    '''class for sound analyzer called in the analyzer'''
    
    handled_types = get_sox_types()
    def __init__(self):
        IAnalyzer.__init__(self)

    def activate(self):
        pass

    def analyze(self, anURI):
        fileid = FileId(filename=os.path.abspath(anURI)) 
        file_descr = FileDescription(file=fileid)
        file_descr.assets = []

        asset_descr = AssetDescription(asset=
        AssetId(subname=os.path.basename(anURI), 
            mimetype=mimetypes.guess_type(anURI, False)[0], file=fileid))

        try:
            pro = subprocess.Popen(['sox', '--i', anURI], stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE)
            out, err = pro.communicate()
            if pro.returncode != 0:
                print("E: SoundAnalyzer failed %swith error code %d! "%(anURI,
                    pro.returncode), out, err)
                return False
        except OSError:
            print("E: SoundAnalyzer failed %s!"%(anURI), out, err)
            return False
        asset_descr.metadata = {}
        meta = {}
        lines = out.strip().split('\n')
        for line in lines:
            line = line.split(':', 1)
            if len(line) == 1:
                line = line[0].split('=')
            line = [l.strip() for l in line]
            if line[0] in ['Input File', 'Comment']: continue
            meta['Sox-'+line[0]] = line[1]
            asset_descr.metadata['Sox-'+line[0]] = MetaDataValue(type=MetaDataType.STRING,
                    string_value=line[1])

        file_descr.assets.append(asset_descr)

        return file_descr
