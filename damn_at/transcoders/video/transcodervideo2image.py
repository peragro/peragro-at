"""Video to Image Transcoder """
import os
from ffvideo import VideoStream
from damn_at.pluginmanager import ITranscoder
from damn_at.options import IntOption, IntVectorOption, expand_path_template

class Video2ImageTranscoder(ITranscoder):
    """Generic Transcoder class for video2image"""
    options = [IntOption(name='second', description='The second from which frame is to be extracted', default=-1),
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

        try:
            stream = VideoStream(file_descr.file.filename)
            if options['second'] > int(stream.duration):
                print "The video is smaller than output frame!", file_descr.file.filename
                return False
            if options['second'] == -1:
                image = stream.get_frame_at_sec(int(stream.duration/2)).image()
            else:
                image = stream.get_frame_at_sec(options['second']).image()
        except OSError:
            print "Cannot open video", file_descr.file.filename
            return False

        full_path = os.path.join(dest_path, file_path)
        if not os.path.exists(os.path.dirname(full_path)):
            os.makedirs(os.path.dirname(full_path))

        if options['size'] != [-1, -1]:
            image.thumbnail(options['size'])
        image.save(full_path)

        return [file_path]
