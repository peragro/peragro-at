import os
from PIL import Image

from damn_at import logger
from damn_at.transcoder import TranscoderException

from damn_at.pluginmanager import ITranscoder
from damn_at.options import IntVectorOption, FloatOption


class ImageTranscoder(ITranscoder):
    convert_map = {"image/jpeg" : {"image/png": [IntVectorOption(name='size', description='The target size of the image', size=2, min=1, max=4096, default=(-1,-1)),
                                                 FloatOption(name='quality', description='The target quality of the image', min=0.0, max=1.0, default=1.0)]
                                  },}
    
    def __init__(self):
        ITranscoder.__init__(self)
        
    def activate(self):
        pass

    def transcode(self, file_paths, asset_id, mimetype, **options):
        return []
