"""
Script to be run with blender -P this
"""
import bpy # pylint: disable=F0401
import binascii
import mimetypes

from damn_at import FileDescription, FileId, AssetDescription, AssetId, MetaDataValue, MetaDataType
from damn_at.serialization import SerializeThriftMsg

def relpath(path, start=None):
    path = bpy.path.relpath(path, start)
    path = path[2:] # Strip leading //
    return path


def main(): # pylint: disable=R0914,R0912,R0915
    """The main method"""
    images = {}
    materials = {}
    meshes = {}
    objects = {}
    texts = {}
    
    # Set up our FileDescription
    fileid = FileId(filename = bpy.path.abspath(bpy.data.filepath))
    file_descr = FileDescription(file=fileid)
    file_descr.assets = []
    
    
    def get_file_id(obj):
        """If the object is in a library, return a file for it, else return this fileid."""
        if obj.library:
            return FileId(filename = relpath(obj.library.filepath))
        return fileid

    """
    Images:
    - Can be packed, so expose them with 'x-blender.image' mimetype.
    """
    for image in bpy.data.images:
        image_fileid = get_file_id(image)
        image_mimetype = mimetypes.guess_type(image.filepath)[0]
        if image.source == 'FILE' and not image.packed_file:
            image_fileid = FileId(filename = relpath(image.filepath, start=image.library.filepath if image.library else None))
        if image.packed_file:
            image_mimetype = 'application/x-blender.image'
        asset_descr = AssetDescription(asset = AssetId(subname = image.name, mimetype = image_mimetype, file = image_fileid))
        if image.packed_file:
            file_descr.assets.append(asset_descr) 
        images[image.name] = asset_descr 


    """
    Materials:
    Have images as dependency.
    """
    for material in bpy.data.materials:
        asset_descr = AssetDescription(asset = AssetId(subname = material.name, mimetype = 'application/x-blender.material', file = get_file_id(material)))
        asset_descr.dependencies = []
        image_names = {}
        for slot in material.texture_slots:
            if slot and slot.texture and slot.texture.type == 'IMAGE' and slot.texture.image:
                image_names[slot.texture.image.name] = None
        for name in image_names:
            if name in images:
                dep = images[name].asset
                asset_descr.dependencies.append(dep)
        file_descr.assets.append(asset_descr) 
        materials[material.name] = asset_descr 


    """
    Meshes:
    Have materials as dependency
    And the images assigned its faces.
    """
    for mesh in bpy.data.meshes:
        mesh.update(calc_tessface=True)
        asset_descr = AssetDescription(asset = AssetId(subname = mesh.name, mimetype = 'application/x-blender.mesh', file = get_file_id(mesh)))
        asset_descr.dependencies = []
        # Collect materials from the mesh
        for material in mesh.materials:
            if material.name in materials:
                dep = materials[material.name].asset
                asset_descr.dependencies.append(dep)
        # Collect images from the faces
        image_names = {}
        for face in mesh.uv_textures:
            for data in face.data:
                if data.image:
                    image_names[data.image.name] = None
        for name in image_names:
            if name in images:
                dep = images[name].asset
                asset_descr.dependencies.append(dep)
        
        asset_descr.metadata = {}
        asset_descr.metadata['nr_of_faces'] = MetaDataValue(type=MetaDataType.INT, int_value=len(mesh.tessfaces))
        asset_descr.metadata['nr_of_vertices'] = MetaDataValue(type=MetaDataType.INT, int_value=len(mesh.vertices))
        asset_descr.metadata['nr_of_polygons'] = MetaDataValue(type=MetaDataType.INT, int_value=len(mesh.polygons))               
        
        file_descr.assets.append(asset_descr) 
        meshes[mesh.name] = asset_descr 


    """
    Objects:
    Has a Mesh as a dependency.
    And materials assigned to the object
    """
    for obj in bpy.data.objects:
        asset_descr = AssetDescription(asset = AssetId(subname = obj.name, mimetype = 'application/x-blender.object', file = get_file_id(obj)))
        asset_descr.dependencies = []
        # Add the mesh as dependency
        if obj.data.name in meshes:
            dep = meshes[obj.data.name].asset
            asset_descr.dependencies.append(dep)
        # Now the materials
        for slot in obj.material_slots:
            if slot and slot.material and slot.link == 'OBJECT':
                if slot.material.name in materials:
                    dep = materials[slot.material.name].asset
                    asset_descr.dependencies.append(dep)
                
        file_descr.assets.append(asset_descr) 
        objects[obj.name] = asset_descr 
     

    """
    Texts:
    Can be packed, so expose them with 'x-blender.text' mimetype.
    """   
    for text in bpy.data.texts:
        text_fileid = get_file_id(text)
        text_mimetype = 'application/x-blender.text'
        if not text.is_in_memory:
            text_fileid = FileId(filename = relpath(text.filepath, start=text.library.filepath if text.library else None))
            text_mimetype = mimetypes.guess_type(text.filepath)[0]
        asset_descr = AssetDescription(asset = AssetId(subname = text.name, mimetype = text_mimetype, file = text_fileid))
        file_descr.assets.append(asset_descr) 
        texts[text.name] = asset_descr
            
    data = SerializeThriftMsg(file_descr)
    print('-**-')
    print(binascii.hexlify(data))
    print('-**-')

if __name__ == '__main__':
    main()
