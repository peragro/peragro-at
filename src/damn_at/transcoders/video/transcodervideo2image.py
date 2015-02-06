"""Video to Image Transcoder """
import os
import tempfile
import subprocess
from PIL import Image
from damn_at.pluginmanager import ITranscoder
from damn_at.options import IntOption, IntVectorOption, expand_path_template

class Video2ImageTranscoder(ITranscoder):
    """Generic Transcoder class for video2image"""
    options = [IntOption(name='second', description='The second from which frame is to be extracted', default=-1, min=-1),
        IntVectorOption(name='size', description='The size of output image in pixels', size=2, min=1, max=4096, default=(-1, -1))]

    convert_map = {"video/mp4" : {"image/png":options, "image/jpeg":options},
            "video/x-msvideo" : {"image/png":options, "image/jpeg":options},
            "video/x-flv" : {"image/png":options, "image/jpeg":options},
            "video/quicktime" : {"image/png":options, "image/jpeg":options},
            "video/x-matroska" : {"image/png":options, "image/jpeg":options},
            "video/mpeg" : {"image/png":options, "image/jpeg":options},
            }

    def __init__(self):
        ITranscoder.__init__(self)

    def activate(self):
        pass

    def transcode(self, dest_path, file_descr,
            asset_id, target_mimetype, **options):

        file_path = expand_path_template(target_mimetype.template,
                target_mimetype.mimetype, asset_id, **options)

        time = file_descr.assets[0].metadata['duration'].string_value.split(':')
        time = eval(time[0])*3600 + eval(time[1])*60 + eval(time[2])
        if time < options['second']:
            print("Not in range of video", file_descr.file.filename)
            return False

        if options['second']==-1:
            second = time/2
        else:
            second = options['second']
        try:
            tmp = tempfile.NamedTemporaryFile(suffix = '.jpeg')
            pro = subprocess.Popen(['ffmpeg', '-ss', str(second), '-i',
                file_descr.file.filename, '-t', '1', '-r', '1', tmp.name, '-y' ])
            out, err = pro.communicate()
            if pro.returncode != 0:
                print('ffmpeg failed %s with error code %d'
                        %(file_descr.file.filename, pro.returncode), err)
                return False
        except OSError:
            print("Cannot open video", file_descr.file.filename)
            return False

        image = Image.open(tmp.name)

        full_path = os.path.join(dest_path, file_path)
        if not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))

        if options['size'] != [-1, -1]:
            image.thumbnail(options['size'])
        image.save(full_path)

        return [file_path]
