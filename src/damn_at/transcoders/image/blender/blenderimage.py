from __future__ import print_function
import os
from PIL import Image

from damn_at import logger
from damn_at.transcoder import TranscoderException

from damn_at.pluginmanager import ITranscoder
from damn_at.options import IntVectorOption, FloatOption, expand_path_template

from damn_at.utilities import script_path, run_blender


class ImageTranscoder(ITranscoder):
    options = [IntVectorOption(name='size', description='The target size of the image', size=2, min=1, max=4096, default=(-1, -1))]
    convert_map = {"application/x-blender.image": {"image/png": options, "image/jpeg": options},
                   "application/x-blender.image": {"image/png": options, "image/jpeg": options},}

    def __init__(self):
        ITranscoder.__init__(self)

    def activate(self):
        pass

    def transcode(self, dest_path, file_descr, asset_id, target_mimetype, **options):

        file_path = expand_path_template(target_mimetype.template, target_mimetype.mimetype, asset_id, **options)
        full_path = os.path.join(dest_path, file_path)

        arguments = ['--', asset_id.subname, full_path]

        stdoutdata, stderrdata, returncode = run_blender(file_descr.file.filename, script_path(__file__), arguments)

        #print(stdoutdata)
        #print(stderrdata)
        #print(returncode) #Todo: check return code

        try:
          im = Image.open(full_path)
        except IOError:
          print(("Cannot open: %s" % full_path))
          return False

        if tuple(options['size']) != (-1, -1):
          im.thumbnail(options['size'])

        if im.mode == 'P':
          im = im.convert('RGB')

        im.save(full_path)

        return [file_path]
