"""Analyzer for audio feature extraction using Essentia"""

from __future__ import print_function
import os
import mimetypes
import subprocess
import json
from damn_at import logger
from damn_at import AssetId, FileId, FileDescription, AssetDescription
from damn_at.pluginmanager import IAnalyzer
from damn_at.analyzers.audio import metadata
import tempfile


def get_supported_formats():
    try:
        pro = subprocess.Popen(['ffmpeg', '-formats'], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out, err = pro.communicate()
        if pro.returncode != 0:
            logger.debug(
                "GetFeatureExtractorTypes failed with error code %d! "
                % pro.returncode,
                out,
                err
            )
            return []
    except OSError as oserror:
        logger.debug("GetFeatureExtractorTypes failed! %s", oserror)
        return []
    extensions = [
        line.split()[1] for line in out.decode("utf-8").split("\n")[4:]
        if len(line.split()) > 1]

    mimes = []
    for ext in extensions:
        mime = mimetypes.guess_type('file.' + ext, False)[0]
        if mime and mime.startswith('audio/'):
            mimes.append(mime)

    return mimes


def get_extracted_ll_features(ofile):
    """returns the extracted low-level features from json file in dictionary format"""

    features = {}
    with open(ofile, 'r') as ef:
        content = json.load(ef)

        if 'rhythm' in content:
            if 'bpm' in content['rhythm']:
                features['bpm'] = content['rhythm']['bpm']
            if 'beats_count' in content['rhythm']:
                features['beats_count'] = content['rhythm']['beats_count']

        if 'tonal' in content:
            if ('chords_key' in content['tonal']
                    and 'chords_scale' in content['tonal']):
                features['chord'] = \
                    str(content['tonal']['chords_key']) + ' ' + \
                    str(content['tonal']['chords_scale'])
            if ('key_key' in content['tonal']
                    and 'key_scale' in content['tonal']):
                features['key'] = \
                    str(content['tonal']['key_key']) + ' ' + \
                    str(content['tonal']['key_scale'])

        if 'lowlevel' in content:
            if 'average_loudness' in content['lowlevel']:
                features['average_loudness'] = \
                    content['lowlevel']['average_loudness']

        if 'metadata' in content:
            if 'audio_properties' in content['metadata']:
                if 'lossless' in content['metadata']['audio_properties']:
                    features['lossless'] = \
                        content['metadata']['audio_properties']['lossless']

    return features


def get_extracted_hl_features(ofile):
    """returns the extracted high-level features from json file in dictionary format"""

    features = {}
    with open(ofile, 'r') as ef:
        content = json.load(ef)

        for f in content['highlevel']:
            features[f] = content['highlevel'][f]['value']

    return features


def extract_feature(ex, in_file, out_file, conf_file=''):
    """Extract feature using 'ex' extractor and stores it to 'out_file'"""

    try:
        pro = subprocess.Popen([ex, in_file, out_file, conf_file],
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        err, out = pro.communicate()
        if pro.returncode != 0:
            print("FeatureExtractor failed with error code %d! "
                  % pro.returncode,
                  out,
                  err)
        else:
            logger.debug("Extracting audio features: \n%s",
                         out.decode("utf-8"))
    except OSError as e:
        print(('E: Feature Extraction failed %s with error %s'
               % (in_file, e)))


class SoundAnalyzer(IAnalyzer):
    """Class for sound analyzer called in the analyzer"""

    handled_types = get_supported_formats()

    def __init__(self):
        IAnalyzer.__init__(self)
        self.ll_ex = 'streaming_extractor_music'
        self.hl_ex = 'essentia_streaming_extractor_music_svm'
        self.conf = os.path.join(os.path.dirname(__file__), 'profile.conf')

    def activate(self):
        pass

    def analyze(self, anURI):
        fileid = FileId(filename=os.path.abspath(anURI))
        file_descr = FileDescription(file=fileid)
        file_descr.assets = []

        asset_descr = AssetDescription(asset=AssetId(
            subname=os.path.basename(anURI),
            mimetype=mimetypes.guess_type(anURI, False)[0],
            file=fileid)
        )
        output_file_ll = tempfile.NamedTemporaryFile(
            suffix='.json',
            prefix=os.path.basename(anURI).split(".")[0] + '_ll',
            dir='/dev/shm',
            delete=True
        )
        output_file_hl = tempfile.NamedTemporaryFile(
            suffix='.json',
            prefix=os.path.basename(anURI).split(".")[0] + '_hl',
            dir='/dev/shm',
            delete=True
        )

        meta = {}
        # low-level features
        extract_feature(self.ll_ex, anURI, output_file_ll.name)
        ll_meta = get_extracted_ll_features(output_file_ll.name)
        meta.update(ll_meta)

        # high-level features
        extract_feature(self.hl_ex, output_file_ll.name, output_file_hl.name, self.conf)
        hl_meta = get_extracted_hl_features(output_file_hl.name)
        meta.update(hl_meta)

        asset_descr.metadata = metadata.MetaDataFeatureExtraction.extract(meta)
        file_descr.assets.append(asset_descr)
        output_file_ll.close()
        output_file_hl.close()

        return file_descr