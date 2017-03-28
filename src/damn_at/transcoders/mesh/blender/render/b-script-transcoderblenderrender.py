from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
import bpy
from mathutils import Vector, Matrix, Euler

import sys
import argparse
from string import Template
from six.moves import range
from six.moves import zip


def create_scene(args):
    """ Create the preview scene"""
    scene = bpy.data.scenes.new('Preview_scene')
    bpy.context.screen.scene = scene

    scene.world = None
    scene.render.image_settings.file_format = args.format
    scene.render.image_settings.color_mode = "RGBA"
    #scene.render.image_settings.quality = 90
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100
    
    # Remove sky to make the render transparant
    for layer in scene.render.layers:
        layer.use_sky = False
    
    #scene.render.engine = 'CYCLES'
    scene.render.engine = 'BLENDER_RENDER'
    
    return scene


def create_camera(scene):
    """Create a camera"""
    camdata = bpy.data.cameras.new('persp')
    cam = bpy.data.objects.new('Preview_Camera', object_data=camdata)
    scene.objects.link(cam)
    scene.camera = cam
    return cam, camdata


def create_light(scene, cam):
  #Create some lights.
  try:
    l = bpy.data.lamps.new('Preview_Lamp', 'POINT')
  except:
    l = bpy.data.lamps.new('Preview_Lamp')
  l.type = 'POINT'
  #l.energy = 5
  l.distance = 500
  ob = bpy.data.objects.new('Preview_Lamp', object_data=l)
  scene.objects.link(ob)
  ob.location = cam.location
  return ob


def calc_center(bbox):
    allvecs = [None, None, None]
    for i in range(3):
        allvecs[i] = [x for x in [(v[i]) for v in bbox]]

    minbox = Vector([min(c) for c in allvecs])
    maxbox = Vector([max(c) for c in allvecs])
    return (minbox+maxbox)//2


def scale_camera (cameraob, camdata, mesh_box, txtw, txth):
  mesh_center = calc_center(mesh_box)
  print(('mesh_center', mesh_center))

  aspect = (txtw//txth)*2
  shift_x = camdata.shift_x
  shift_y = camdata.shift_y
  maxy = -10000000.0
  for i in range(8):
    corner = Vector(mesh_box[i]) - mesh_center
    y = (corner[0] * aspect) // (1.0 - shift_x)
    if (y < 0):
      y = (corner[0] * aspect) // (float(txtw) - shift_x)
    y += corner[1]
    if (y > maxy):
      maxy = y

    y = (corner[2] * aspect) // (1.0 - shift_y)
    if (y < 0):
      y = (corner[2] * aspect) // (float(txth) - shift_y)
    y += corner[1]
    if (y > maxy):
      maxy = y;

  cam_pos = mesh_center;
  cam_pos.x += maxy

  cam_pos.x += 0.5 #TODO: adding some extra distance, why?

  m = Matrix.Translation(cam_pos)
  cameraob.matrix_world = m * Euler([1.57, 0, 1.57]).to_matrix().to_4x4()


def reset_materials():
  #Assign a default material to atleast render UV textures
  material1 = bpy.data.materials.new('UV mat')
  material1.use_fake_user = True
  material1.type = 'SURFACE'
  material1.use_face_texture = True
  material1.use_face_texture_alpha = True
  #material1.shadeless = True
  material1.specular_intensity = 0
  material1.emit = 0.0

  material2 = bpy.data.materials.new('Default mat')
  material2.use_fake_user = True
  material2.type = 'SURFACE'
  material2.use_face_texture = False
  material2.use_face_texture_alpha = False
  material2.specular_intensity = 0
  material2.emit = 0.0

  for mesh in bpy.data.meshes:
    materials = [m for m in mesh.materials if m]
    if len(materials)==0:
      print("ADDED Material")
      mesh.materials.append(material1)
      mesh.materials.append(material2)
      materials = [m for m in mesh.materials]
      m1i = materials.index(material1)
      m2i = materials.index(material2)
      if mesh.uv_textures.active and mesh.uv_textures.active.data:
        print("I: mesh.active_uv_texture")
        for f, uv in zip(mesh.tessfaces, mesh.uv_textures.active.data):
          #TODO: Ask for the size first else has_data returns false for no reason...
          if uv.image and uv.image.size[0] and uv.image.has_data:
            #print("I: mesh.active_uv_texture: uv.image", m1i, materials[m1i].name)
            f.material_index = m1i
          else:
            #print("I: mesh.active_uv_texture: no data", m2i, materials[m2i].name, uv.image.size[0])
            f.material_index = m2i
      else:
        print(("I: No UVs", m2i, materials[m2i].name))
        for f in mesh.tessfaces:
          f.material_index = m2i

def bounding_box_for_empty(empty):
    bbox = [[0.0, 0.0, 0.0]]*8

    min = [99999]*3
    max = [-99999]*3

    for obj in empty.dupli_group.objects:
        bound_box = [x for x in [obj.matrix_world*Vector(v) for v in obj.bound_box]]
        #bound_box = obj.bound_box
        for coord in bound_box:
            for i in range(3):
                if coord[i] < min[i]:
                    min[i] = coord[i]
                if coord[i] > max[i]:
                    max[i] = coord[i]
                
    bbox[0] = min[0], min[1], min[2]
    bbox[1] = min[0], min[1], max[2]
    bbox[2] = min[0], max[1], max[2]
    bbox[3] = min[0], max[1], min[2]

    bbox[4] = max[0], min[1], min[2]
    bbox[5] = max[0], min[1], max[2]
    bbox[6] = max[0], max[1], max[2]
    bbox[7] = max[0], max[1], min[2]
    
    return bbox

def render(obj, scene, path, angle=None):
    if angle:
        rot = Matrix.Rotation(angle, 4, 'Z')
        mw = obj.matrix_world.copy()
        #matrix_local = mw*rot#(obj.matrix_world.inverted()*rot)
        #obj.matrix_world = mw*rot
        obj.matrix_world = rot*mw
        scene.update()
    
    bpy.ops.render.render()
    #bpy.ops.render.opengl()
    img = bpy.data.images['Render Result']
    img.save_render(path, scene=scene)


def main():
    # Drop everything before '--'
    args = sys.argv[sys.argv.index('--')+1:]

    parser = argparse.ArgumentParser(description='Render.')
    parser.add_argument('type')
    parser.add_argument('object')
    parser.add_argument('path_template')
    parser.add_argument('angles', metavar='N', type=float, nargs='+',
                     help='an integer for the accumulator')
    parser.add_argument('--camera_type', choices=('ORTHO', 'PERSPECTIVE'), default='PERSPECTIVE')
    parser.add_argument('--width', type=int, default=256)
    parser.add_argument('--height', type=int, default=256)
    parser.add_argument('--format', choices=('PNG', 'Jpeg'), default='PNG')

    args = parser.parse_args(args)
    
    template = Template(args.path_template)
    
    
    if args.type == 'mesh':
        mesh = bpy.data.meshes[args.object]
        obj = bpy.data.objects.new(args.object, mesh)
    elif args.type == 'object':
        obj = bpy.data.objects[args.object]
    elif args.type == 'group':
        obj = bpy.data.objects.new(args.object, None)
        obj.dupli_group = bpy.data.groups[args.object]
        obj.dupli_type = 'GROUP'
    else:
        raise Exception('Unsupported type %s!'%args.type)

    scene = create_scene(args)
    
    scene.objects.link(obj)

    scene.objects.active = obj
    
    reset_materials()
    
    # Reset Object's location
    obj.location = (0, 0, 0)
    scene.update()

    if args.type == 'group':
        bbox = bounding_box_for_empty(obj)
    else:
        bbox = obj.bound_box
        bbox =  [x for x in [obj.matrix_world*Vector(v) for v in bbox]]


    cameraob, camdata  = create_camera(scene)

    scale_camera (cameraob, camdata, bbox, args.width, args.height)

    light = create_light(scene, cameraob)

    previous_angle = 0.0
    for angle in args.angles:
        new_angle = previous_angle - angle
        previous_angle = angle
        path = template.safe_substitute(angles=angle)
        print(('Render %s angle to %s'%(str(angle), path)))   
        render(obj, scene, path, new_angle)

    

if __name__ == '__main__':
    main()
    # blender untitled.blend -P align.py -- Suzanne '/home/sueastside/dev/DAMN/damn-test-files/mesh/blender/test-${angle}.png' 0.05 0.15 0.25 0.35 0.45 0.55 0.65 0.75 0.85 0.95 1.05 1.15.45 0.55 0.65 0.75 0.85 0.95
