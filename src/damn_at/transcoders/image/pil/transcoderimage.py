import os
from PIL import Image

from damn_at import logger
from damn_at.transcoder import TranscoderException

from damn_at.pluginmanager import ITranscoder
from damn_at.options import IntVectorOption, FloatOption, expand_path_template


class ImageTranscoder(ITranscoder):
    options = [IntVectorOption(name='size', description='The target size of the image', size=2, min=1, max=4096, default=(-1,-1)),
               FloatOption(name='quality', description='The target quality of the image', min=0.0, max=1.0, default=1.0)]
    convert_map = {"image/jpeg" : {"image/png": options, "image/jpeg": options, "image/x-ms-bmp" : options},
                   "image/png" : {"image/png": options, "image/jpeg": options, "image/x-ms-bmp": options},
                   "image/x-ms-bmp" : {"image/x-ms-bmp": options, "image/png": options, "image/jpeg": options} }
    
    def __init__(self):
        ITranscoder.__init__(self)
        
    def activate(self):
        pass

    def transcode(self, dest_path, file_descr, asset_id, target_mimetype, **options):
        file_path = expand_path_template(target_mimetype.template, target_mimetype.mimetype, asset_id, **options)
        
        try:  
          im = Image.open(file_descr.file.filename)
        except IOError:
          print "cannot open", file_descr.file.fileName
          return False

        if options['size'] != [-1,-1]:
          im.thumbnail(options['size'])
        
        if im.mode == 'P':
          im = im.convert('RGB')
          
        full_path = os.path.join(dest_path, file_path)
        if not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))
          
        im.save(full_path)
        
        return [file_path]
