import os
import wave, struct, json

from damn_at import logger
from damn_at.transcoder import TranscoderException

from damn_at.pluginmanager import ITranscoder
from damn_at.options import IntOption, FloatOption, expand_path_template

class Audio2ImageTranscoder(ITranscoder):
    options = [IntOption(name = 'channels', description = 'Number of channels to output', default = 2, min=1, max=2)]
    convert_map = {"audio/x-wav" : {"application/json" : options}}

    def __init__(self):
        ITranscoder.__init__(self)

    def activate(self):
        pass

    def transcode(self, dest_path, file_descr, asset_id, target_mimetype,
            **options):

        file_path = expand_path_template(target_mimetype.template,
                target_mimetype.mimetype, asset_id, **options)

        try:
            stream = wave.open(file_descr.file.filename, "rb")
        except IOError:
            print "cannot open", file_descr.file.filename
            return false
        
        num_channels = stream.getnchannels()
        sample_width = stream.getsampwidth()
        num_frames = stream.getnframes()

        raw_data = stream.readframes(num_frames)
        stream.close()
        
        total_samples = num_channels*num_frames

        if sample_width == 1:
            fmt = "%iB" % total_samples # read unsigned chars
        elif sample_width == 2:
            fmt = "%ih" % total_samples # read signed 2 byte shorts
        else:
            raise ValueError("Only supports 8 and 16 bit audio formats.")

        integer_data = struct.unpack(fmt, raw_data)
        del raw_data # Keep memory tidy

        channels = [ [] for time in range(num_channels) ]

        for index, value in enumerate(integer_data):
            bucket = index % num_channels
            channels[bucket].append(value)

        if num_channels == options['channels']:
            if options['channels'] == 1:
                transcoded = json.dumps({"mono": channels[0]}, indent=4, separators=(',', ': '))
            elif options['channels'] ==2:
                transcoded = json.dumps({"left": channels[0], "right":
                    channels[1]}, indent=4, separators=(',', ': '))

        else:
            if options['channels'] == 1:
                transcoded = json.dumps({"mono": channels[0]}, indent=4, separators=(',', ': '))
            else :
                transcoded = json.dumps({"left": channels[0], "right":
                    channels[0]}, indent=4, separators=(',', ': '))
        
        full_path = os.path.join(dest_path, file_path)
        if not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))

        output_file = open(full_path, 'w')
        output_file.write(transcoded)
        output_file.close()

        return [file_path]
