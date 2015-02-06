import os
import subprocess

from string import Template

from damn_at import logger
from damn_at.transcoder import TranscoderException

from damn_at.pluginmanager import ITranscoder
from damn_at.options import IntVectorOption, IntOption, expand_path_template
from damn_at.utilities import script_path, run_blender


class BlenderTranscoder(ITranscoder):
    options = [
        IntVectorOption(
            name='size',
            description='The target size of the image',
            size=2,
            min=1,
            max=4096,
            default=(128, 128)
        ),
        IntOption(
            name='pages',
            description='Total number of frames.',
            min=1,
            max=4096,
            default=1
        ),
    ]
    convert_map = {
        "application/x-blender.text": {
            "image/jpg": options,
            "image/png": options
        },
    }

    def __init__(self):
        ITranscoder.__init__(self)

    def activate(self):
        pass

    def transcode(self, dest_path, file_descr,
                  asset_id, target_mimetype, **options):
        path_template = expand_path_template(
            target_mimetype.template,
            target_mimetype.mimetype,
            asset_id,
            **options
        )
        abs_file_path = os.path.join(dest_path, path_template)
        abs_file_path_txt = abs_file_path+'.txt'

        arguments = [
            '--',
            asset_id.mimetype,
            asset_id.subname,
            abs_file_path_txt
        ]

        logger.debug(abs_file_path)

        stdoutdata, stderrdata, returncode = run_blender(
            file_descr.file.filename,
            script_path(__file__),
            arguments
        )

        logger.debug(stdoutdata)
        logger.debug(stderrdata)
        logger.debug(returncode)
        #print(returncode) #Todo: check return code

        arguments = [
            'convert',
            '-pointsize',
            '26',
            '-resize',
            str(options['size'][0]),
            abs_file_path_txt + '[0]',
            abs_file_path
        ]
        # print arguments
        pro = subprocess.Popen(
            arguments,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdoutdata, stderrdata = pro.communicate()
        logger.debug(stdoutdata)
        logger.debug(stderrdata)
        logger.debug(pro.returncode)

        return [path_template]
