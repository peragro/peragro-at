from __future__ import absolute_import
from __future__ import print_function
import os
import tempfile
import json
import mimetypes
import subprocess

from damn_at import logger
from damn_at.transcoder import TranscoderException
from damn_at.utilities import WaveData

from damn_at.pluginmanager import ITranscoder
from damn_at.options import IntOption, expand_path_template
from io import open


class Audio2JsonTranscoder(ITranscoder):
    options = [IntOption(name='channels',
                         description='Number of channels to output',
                         default=2, min=1, max=2),
               IntOption(name='samplerate',
                         description='Samples per second each channel',
                         default=800, min=200),
               IntOption(name='precision',
                         description='Decimal Precision',
                         default=2, min=1)]

    convert_map = {"audio/x-wav": {"application/json": options},
                   "audio/mpeg": {"application/json": options}}

    def __init__(self):
        ITranscoder.__init__(self)

    def activate(self):
        pass

    def transcode(self, dest_path, file_descr, asset_id,
                  target_mimetype, **options):

        file_path = expand_path_template(target_mimetype.template,
                                         target_mimetype.mimetype,
                                         asset_id, **options)

        audio_mimetype = mimetypes.guess_type(file_descr.file.filename)[0]
        try:
            tmp = tempfile.NamedTemporaryFile()
            pro = subprocess.Popen(["sox", file_descr.file.filename,
                                    "-t", "wav", "-r",
                                    str(options['samplerate']), tmp.name],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            out, err = pro.communicate()
            if pro.returncode != 0:
                print(("Sox failed %s with error code %d!"
                       % (file_descr.file.filename, pro.returncode), out, err))
                return False
            else:
                toopen = tmp.name
        except OSError:
            print(("Sox failed %s!" % file_descr.file.filename, out, err))
            return False

        wavedata = WaveData()
        wavedata.extractData(toopen, options['precision'])
        channels = wavedata.getData()

        if wavedata.nchannels == options['channels']:
            if options['channels'] == 1:
                transcoded = json.dumps({"mono": channels[0]})
            elif options['channels'] == 2:
                transcoded = json.dumps({"left": channels[0],
                                         "right": channels[1]})

        else:
            if options['channels'] == 1:
                transcoded = json.dumps({"mono": channels[0]})
            else:
                transcoded = json.dumps({"left": channels[0],
                                         "right": channels[0]})

        full_path = os.path.join(dest_path, file_path)
        if not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))

        output_file = open(full_path, 'w')
        output_file.write(transcoded)
        output_file.close()

        return [file_path]
