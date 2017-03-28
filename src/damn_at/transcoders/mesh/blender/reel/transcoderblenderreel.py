from __future__ import division
from __future__ import absolute_import
import os
from PIL import Image

from string import Template

from damn_at import logger
from damn_at.transcoder import TranscoderException

from damn_at.pluginmanager import ITranscoder
from damn_at.options import IntVectorOption, IntOption, expand_path_template
from damn_at.utilities import script_path, run_blender
from six.moves import map
from six.moves import range

class BlenderTranscoder(ITranscoder):
    options = [IntVectorOption(name='size', description='The target size of the image', size=2, min=1, max=4096, default=(128, 128)),
               IntOption(name='frames', description='Total number of frames.', min=1, max=4096, default=12),
               IntOption(name='footage', description='Number of frames per line', min=1, max=4096, default=4),]
    convert_map = {"application/x-blender.object": {"image/jpg-reel": options, "image/png-reel": options},
                   "application/x-blender.mesh": {"image/jpg-reel": options, "image/png-reel": options},
                   "application/x-blender.group": {"image/jpg-reel": options, "image/png-reel": options},}
    
    def __init__(self):
        ITranscoder.__init__(self)
        
    def activate(self):
        pass

    def transcode(self, dest_path, file_descr, asset_id, target_mimetype, **options):
        path_template = expand_path_template(target_mimetype.template, target_mimetype.mimetype, asset_id, **options)
        abs_file_path = os.path.join(dest_path, path_template)
        template = Template(path_template+'__${angles}')
        
        angles = [0.0, 0.1, 0.5]
        
        width = options['size'][0] * options['footage']
        height = options['size'][1] * (options['frames']//options['footage'])
          
        angles = []
        file_paths = []
        for angle in range(0, 628, 628//12):
            angle = angle//100.0
            file_path = template.safe_substitute(angles=angle)
            file_paths.append(file_path)
            angles.append(angle)
            
        if asset_id.mimetype == 'application/x-blender.mesh':
            datatype = 'mesh' 
        elif asset_id.mimetype == 'application/x-blender.group':
            datatype = 'group' 
        else:
            datatype = 'object' 
            
        arguments = ['--', datatype, asset_id.subname, os.path.join(dest_path, template.safe_substitute())]
        arguments.extend(list(map(str, angles)))
        arguments.append('--format=PNG')#TODO
        arguments.append('--camera_type=PERSPECTIVE')
        arguments.append('--width='+str(options['size'][0]))
        arguments.append('--height='+str(options['size'][1]))
        
        script = os.path.join(os.path.dirname(__file__), '../render/b-script-transcoderblenderrender.py')
        
        logger.debug(abs_file_path)
            
        stdoutdata, stderrdata, returncode = run_blender(file_descr.file.filename, script, arguments)
        
        logger.debug(stdoutdata)
        logger.debug(stderrdata)
        logger.debug(returncode)
        #print(returncode) #Todo: check return code
        
        sprite = Image.new('RGB', (width, height))
        for i, file_path in enumerate(file_paths):
            path = os.path.join(dest_path, file_path)
            tile = Image.open(path)
            x = (i%options['footage'])*options['size'][0]
            y = (i//options['footage'])*options['size'][1]
            sprite.paste(tile, (x, y))
        
        #sprite.show()    
        sprite.save(abs_file_path)
        
        return [path_template]
