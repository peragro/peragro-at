import wave, struct

class WaveData():
    
    def __init__(self):
        self.channels = None
        self.nchannels = None
    
    def extractData(self, path, precision):
        stream = wave.open(path, 'rb')
        self.nchannels = stream.getnchannels()
        sample_width = stream.getsamplewidth()
        num_frames = stream.getnframes()

        raw_data = stream.readframes(num_frames)
        stream.close()

        total_samples = self.nchannels*num_frames

        if sample_width == 1:
            fmt = "%iB" % total_samples # read unsigned chars
            round_with = 256.0
        elif sample_width == 2:
            fmt = "%ih" % total_samples # read signed 2 byte shorts
            round_with = 32768.0
        else:
            raise ValueError("Only supports 8 and 16 bit audio formats.")

        integer_data = struct.unpack(fmt, raw_data)
        del raw_data # Keep Memory Tidy

        self.channels = [ [] for time in range(self.nchannels) ]

        for index, value in enumerate(integer_data):
            bucket = index % self.nchannels
            self.channels[bucket].append(round(), precision)

    def getData(self):
        return self.channels
