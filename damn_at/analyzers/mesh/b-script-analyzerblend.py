import bpy

import sys, os
import b2cs
print("Loading B2CS")

def FileName(object):
  return os.path.normpath(bpy.path.abspath(object.filepath)).replace('\\', '/')

#==============================================
def GetDependencies2(self):
  deps = self.GetDependencies()
  
  newdeps = {'T':{}, 'M':{}, 'F':{}, 'G':{}, }
  
  for name, tex in deps['T'].items():
    if tex.packed_file:
      newdeps['T'][tex.name] = False
    else:
      newdeps['T'][tex.name] = FileName(tex)
      
  return newdeps

b2cs.io.object.Hierarchy.GetDependencies2 = GetDependencies2
#==============================================

#print = lambda x: sys.stdout.write(str(x))

objects = {}
for object in [o for o in bpy.data.objects if o.type=='MESH' and not o.parent]:
  d = {'metadata': {}, }
  d['dependencies'] = b2cs.io.object.Hierarchy(object, None).GetDependencies2()
  d['metadata']['blender-object-type'] = str(object.type)
  if object.type=='MESH':
    d['metadata']['faces'] = len(object.data.faces)
    d['metadata']['vertices'] = len(object.data.vertices)
    d['metadata']['edges'] = len(object.data.edges)
    d['metadata']['materials'] = len(object.data.materials)
  objects[object.name] = d


textures = {}
for image in [o for o in bpy.data.images]:
  d = {'metadata': {}, }
  d['fileName'] = FileName(image)
  d['packed'] = bool(image.packed_file)
  if d['packed']:
    d['metadata']['blender-image-format'] = image.file_format
    d['metadata']['resolution-width'] = image.size[0]
    d['metadata']['resolution-height'] = image.size[1]
  
  textures[image.name] = d
 
 
assets = {'objects': objects, 'textures': textures}

print('----\n')
print(assets)
print('\n----\n')
