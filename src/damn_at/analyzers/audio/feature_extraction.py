'''Analyzer for audio feature extraction using Essentia'''
from __future__ import print_function
import os
import mimetypes
import subprocess
import json
from damn_at import logger
from damn_at import AssetId, FileId, FileDescription, AssetDescription
from damn_at.pluginmanager import IAnalyzer
from damn_at.analyzers.audio import metadata


def get_supported_formats():
    try:
        pro = subprocess.Popen(['ffmpeg', '-formats'], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, err = pro.communicate()
        if pro.returncode != 0:
            logger.debug(
                "GetFeatureExtractorTypes failed with error code %d! ", pro.returncode,
                out,
                err
            )
            return []
    except OSError as oserror:
        logger.debug("GetFeatureExtractorTypes failed! %s", oserror)
        return []
    extensions = [line.split()[1] for line in out.decode("utf-8").split("\n")[4:] if len(line.split()) > 1]
    mimes = []
    for ext in extensions:
        mime = mimetypes.guess_type('file.' + ext, False)[0]
        if mime and mime.startswith('audio/'):
            mimes.append(mime)
    return mimes

def get_extracted_features(ofile):
    '''returns the extracted features from json file in dictionary format'''
    features = {}
    with open(ofile, 'r') as ef:
        content = json.load(ef)
        if 'rhythm' in content:
            if 'bpm' in content['rhythm']:
                features['bpm'] = content['rhythm']['bpm']
            if 'beats_count' in content['rhythm']:
                features['beats_count'] = content['rhythm']['beats_count']
        if 'tonal' in content:
            if 'chords_key' in content['tonal'] and 'chords_scale' in content['tonal']:
                features['chord'] = str(content['tonal']['chords_key']) + str(content['tonal']['chords_scale'])
            if 'key_key' in content['tonal'] and 'key_scale' in content['tonal']:
                features['key'] = str(content['tonal']['key_key']) + str(content['tonal']['key_scale'])

    return features

class SoundAnalyzer(IAnalyzer):
    '''Class for sound analyzer called in the analyzer'''

    handled_types = get_supported_formats()

    def __init__(self):
        IAnalyzer.__init__(self)
        self.ex = os.path.join(os.path.dirname(__file__), 'extractors/streaming_extractor_music')

    def activate(self):
        pass

    def analyze(self, anURI):
        fileid = FileId(filename=os.path.abspath(anURI))
        file_descr = FileDescription(file=fileid)
        file_descr.assets = []

        asset_descr = AssetDescription(asset=AssetId(subname=os.path.basename(anURI),
                                       mimetype=mimetypes.guess_type(anURI, False)[0],
                                       file=fileid))

        output_file = os.path.abspath(anURI).split(".")[0] + ".json"

        try:
            if os.path.exists(self.ex):
                subprocess.call([self.ex, anURI, output_file])
            else:
                print("E: Extractor does not exist, please place the extractor at 'damn_at/analyzers/audio/extractor'")
        except Exception as e:
            print(("E: Feature Extraction failed %s with error %s" % (anURI, e)))

        meta = get_extracted_features(output_file)
        asset_descr.metadata = metadata.MetaDataFeatureExtraction.extract(meta)
        file_descr.assets.append(asset_descr)

        return file_descr
