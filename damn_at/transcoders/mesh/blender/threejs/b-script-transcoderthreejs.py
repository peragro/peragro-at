import bpy
from mathutils import Vector, Matrix, Euler

import os, sys
import argparse

from export_threejs import export_mesh


# ################################################################
# Custom properties
# ################################################################
from bpy.props import EnumProperty

bpy.types.Object.THREE_castShadow = bpy.props.BoolProperty()
bpy.types.Object.THREE_receiveShadow = bpy.props.BoolProperty()
bpy.types.Object.THREE_doubleSided = bpy.props.BoolProperty()
bpy.types.Object.THREE_exportGeometry = bpy.props.BoolProperty(default = True)

bpy.types.Material.THREE_useVertexColors = bpy.props.BoolProperty()
bpy.types.Material.THREE_depthWrite = bpy.props.BoolProperty(default = True)
bpy.types.Material.THREE_depthTest = bpy.props.BoolProperty(default = True)

THREE_material_types = [("Basic", "Basic", "Basic"), ("Phong", "Phong", "Phong"), ("Lambert", "Lambert", "Lambert")]
bpy.types.Material.THREE_materialType = EnumProperty(name = "Material type", description = "Material type", items = THREE_material_types, default = "Lambert")

THREE_blending_types = [("NoBlending", "NoBlending", "NoBlending"), ("NormalBlending", "NormalBlending", "NormalBlending"),
                        ("AdditiveBlending", "AdditiveBlending", "AdditiveBlending"), ("SubtractiveBlending", "SubtractiveBlending", "SubtractiveBlending"),
                        ("MultiplyBlending", "MultiplyBlending", "MultiplyBlending"), ("AdditiveAlphaBlending", "AdditiveAlphaBlending", "AdditiveAlphaBlending")]
bpy.types.Material.THREE_blendingType = EnumProperty(name = "Blending type", description = "Blending type", items = THREE_blending_types, default = "NormalBlending")


def main():
    # Drop everything before '--'
    args = sys.argv[sys.argv.index('--')+1:]

    parser = argparse.ArgumentParser(description='Render.')
    parser.add_argument('object')
    parser.add_argument('path_template')
    
    args = parser.parse_args(args)
    
    scene = bpy.context.scene
    objects = [bpy.data.objects[args.object]]
    filepath = args.path_template
    
    dst_dir = os.path.dirname(filepath)
    if not os.access(dst_dir, os.R_OK|os.W_OK|os.X_OK):
        os.makedirs(dst_dir)
    
    option_flip_yz = True
    option_vertices = True
    option_vertices_truncate = False
    option_faces = True
    option_normals = True
    option_uv_coords = True
    option_materials = True
    option_colors = True
    option_bones = True
    option_skinning = True
    align_model = 0
    option_export_scene = False
    option_lights = False
    option_cameras = False
    option_scale = 1.0
    option_url_base_html = False
    option_copy_textures = True   #TODO, don't copy textures, use asset_id references instead!
    option_animation_morph = False
    option_animation_skeletal = False
    option_frame_step = 1
    
    export_mesh(objects, scene, filepath,
                    option_vertices,
                    option_vertices_truncate,
                    option_faces,
                    option_normals,
                    option_uv_coords,
                    option_materials,
                    option_colors,
                    option_bones,
                    option_skinning,
                    align_model,
                    option_flip_yz,
                    option_scale,
                    True,            # export_single_model
                    option_copy_textures,
                    option_animation_morph,
                    option_animation_skeletal,
                    option_frame_step)


if __name__ == '__main__':
    main()
