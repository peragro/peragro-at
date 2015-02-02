import os
from PIL import Image

from damn_at import logger
from damn_at.transcoder import TranscoderException

from damn_at.pluginmanager import ITranscoder
from damn_at.options import IntVectorOption, EnumOption, expand_path_template
from damn_at.utilities import script_path, run_blender

class BlenderMaterialTranscoder(ITranscoder):
    options = [IntVectorOption(name='size', description='The target size of the image', size=2, min=1, max=4096, default=(64,64))]
    convert_map = {"application/x-blender.material" : {"image/jpg": options},
                   "application/x-blender.material" : {"image/png": options},}
    
    def __init__(self):
        ITranscoder.__init__(self)
        
    def activate(self):
        pass

    def transcode(self, dest_path, file_descr, asset_id, target_mimetype, **options):
        
        path_template = expand_path_template(target_mimetype.template, target_mimetype.mimetype, asset_id, **options)
        path_template = os.path.join(dest_path, path_template)
            
        arguments = ['--', file_descr.file.filename, asset_id.subname, path_template]
        arguments.append('--format=PNG')#TODO
        arguments.append('--width='+str(options['size'][0]))
        arguments.append('--height='+str(options['size'][1]))
            
        stdoutdata, stderrdata, returncode = run_blender(os.path.join(os.path.dirname(__file__), 'BlenderMaterialPreviewScenes.blend'), script_path(__file__), arguments)
        
        logger.debug(stdoutdata)
        logger.debug(stderrdata)
        logger.debug(returncode)
        #print(returncode) #Todo: check return code
        
        return path_template
