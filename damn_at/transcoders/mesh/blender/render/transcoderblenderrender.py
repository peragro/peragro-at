import os
from PIL import Image

from damn_at import logger
from damn_at.transcoder import TranscoderException

from damn_at.pluginmanager import ITranscoder
from damn_at.options import IntVectorOption, FloatArrayOption, EnumOption, expand_path_template
from damn_at.utilities import script_path, run_blender

class BlenderTranscoder(ITranscoder):
    options = [IntVectorOption(name='size', description='The target size of the image', size=2, min=1, max=4096, default=(64,64)),
               EnumOption(name='camera_type', description='The camera type', choices=('ORTHO', 'PERSPECTIVE'), default='PERSPECTIVE'),
               FloatArrayOption(name='angles', description='The angle', min=0.0, max=3.1415, default=(0.0,))]
    convert_map = {"application/x-blender.object" : {"image/jpg": options},
                   "application/x-blender.object" : {"image/png": options},
                   "application/x-blender.mesh" : {"image/jpg": options},
                   "application/x-blender.mesh" : {"image/png": options},
                   "application/x-blender.group" : {"image/jpg": options},
                   "application/x-blender.group" : {"image/png": options},}
    
    def __init__(self):
        ITranscoder.__init__(self)
        
    def activate(self):
        pass

    def transcode(self, dest_path, file_descr, asset_id, target_mimetype, **options):
        angles = options['angles']
        del options['angles']
        
        path_template = expand_path_template(target_mimetype.template, target_mimetype.mimetype, asset_id, **options)
        path_template = os.path.join(dest_path, path_template)
        
        file_paths = []
        for angle in angles:
            opts = dict(options)
            opts['angles'] = angle
            file_path = expand_path_template(target_mimetype.template, target_mimetype.mimetype, asset_id, **opts)
            file_paths.append(file_path)
            
        if asset_id.mimetype == 'application/x-blender.mesh':
            datatype = 'mesh' 
        elif asset_id.mimetype == 'application/x-blender.group':
            datatype = 'group' 
        else:
            datatype = 'object' 
            
        arguments = ['--', datatype, asset_id.subname, path_template]
        arguments.extend(map(str, angles))
        arguments.append('--format=PNG')#TODO
        arguments.append('--camera_type=PERSPECTIVE')
        arguments.append('--width='+str(options['size'][0]))
        arguments.append('--height='+str(options['size'][1]))
        
        
            
        stdoutdata, stderrdata, returncode = run_blender(file_descr.file.filename, script_path(__file__), arguments)
        
        logger.debug(stdoutdata)
        logger.debug(stderrdata)
        logger.debug(returncode)
        #print(returncode) #Todo: check return code
        
        return file_paths
