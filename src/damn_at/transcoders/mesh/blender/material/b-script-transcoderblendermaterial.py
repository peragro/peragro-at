import bpy
from mathutils import Vector, Matrix, Euler

import sys
import argparse


def render(scene, path):
    bpy.ops.render.render()
    # bpy.ops.render.opengl()
    img = bpy.data.images['Render Result']
    img.save_render(path, scene=scene)


def main():
    # Drop everything before '--'
    args = sys.argv[sys.argv.index('--')+1:]

    parser = argparse.ArgumentParser(description='Render.')
    parser.add_argument('filepath')
    parser.add_argument('name')
    parser.add_argument('path_template')
    parser.add_argument('--width', type=int, default=256)
    parser.add_argument('--height', type=int, default=256)
    parser.add_argument('--format', choices=('PNG', 'Jpeg'), default='PNG')

    args = parser.parse_args(args)

    bpy.ops.wm.link_append(filepath="/appended.blend/Material/"+args.name,
                           filename=args.name,
                           directory=args.filepath+"/Material/",
                           link=False)

    mat = bpy.data.materials[args.name]
    obj = bpy.data.objects['SolidModel']

    scene = bpy.context.screen.scene

    obj.data.materials.clear()
    obj.data.materials.append(mat)

    # Decrease quality settings a bit
    # scene.render.use_antialiasing = False
    # scene.render.use_sss = False

    scene.render.image_settings.file_format = args.format
    scene.render.image_settings.color_mode = "RGBA"
    # scene.render.image_settings.quality = 90
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100

    # scene.render.engine = 'CYCLES'
    scene.render.engine = 'BLENDER_RENDER'

    render(scene, args.path_template)


if __name__ == '__main__':
    main()
