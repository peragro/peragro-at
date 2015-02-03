import os
from PIL import Image

from damn_at import logger
from damn_at.transcoder import TranscoderException

from damn_at.pluginmanager import ITranscoder
from damn_at.options import IntVectorOption, EnumOption, expand_path_template
from damn_at.utilities import script_path, run_blender

class BlenderThreeJSTranscoder(ITranscoder):
    options = []
    convert_map = {"application/x-blender.object" : {"application/json": options},}
    
    def __init__(self):
        ITranscoder.__init__(self)
        
    def activate(self):
        pass

    def transcode(self, dest_path, file_descr, asset_id, target_mimetype, **options):
        
        path_template = expand_path_template(target_mimetype.template, target_mimetype.mimetype, asset_id, **options)
        path_template = os.path.join(dest_path, path_template)
            
        arguments = ['--', asset_id.subname, path_template]
            
        stdoutdata, stderrdata, returncode = run_blender(file_descr.file.filename, script_path(__file__), arguments)
        
        logger.debug(stdoutdata)
        logger.debug(stderrdata)
        logger.debug(returncode)
        #print(returncode) #Todo: check return code
        
        return path_template
