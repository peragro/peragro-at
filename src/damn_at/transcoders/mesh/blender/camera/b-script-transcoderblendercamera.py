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
    parser.add_argument('object')
    parser.add_argument('path_template')
    parser.add_argument('--width', type=int, default=256)
    parser.add_argument('--height', type=int, default=256)
    parser.add_argument('--format', choices=('PNG', 'Jpeg'), default='PNG')

    args = parser.parse_args(args)

    camera = bpy.data.objects[args.object]

    scene = camera.users_scene[0]

    scene.camera = camera  # Set active camera

    bpy.context.screen.scene = scene

    # scene.world = None
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
