from damn_at.metadata import MetaDataExtractor
from damn_at import MetaDataType


class MetaDataBlenderImage(MetaDataExtractor):
    __mimetype__ = 'application/x-blender.image'

    channels = MetaDataType.INT, lambda context: context['image'].channels
    depth = MetaDataType.INT, lambda context: context['image'].depth
    file_format = MetaDataType.STRING, lambda context: str(context['image'].file_format)
    # resolution = MetaDataType.STRING, lambda context: '{}x{}'.format(*list(context['image'].resolution[:]))
    size = MetaDataType.STRING, lambda context: '{}x{}'.format(*list(context['image'].size[:]))


class MetaDataBlenderMesh(MetaDataExtractor):
    __mimetype__ = 'application/x-blender.mesh'

    nr_of_faces = MetaDataType.INT, lambda context: len(context['mesh'].tessfaces)
    nr_of_vertices = MetaDataType.INT, lambda context: len(context['mesh'].vertices)
    nr_of_polygons = MetaDataType.INT, lambda context: len(context['mesh'].polygons)


class MetaDataBlenderObject(MetaDataExtractor):
    __mimetype__ = 'application/x-blender.object'

    location = MetaDataType.STRING, lambda context: str(context['object'].location)
    type = MetaDataType.STRING, lambda context: str(context['object'].type)
    dimensions = MetaDataType.STRING, lambda context: str(context['object'].dimensions)


class MetaDataWaveFrontDefault(MetaDataExtractor):
    __mimetype__ = 'application/wavefront-obj'

    nr_of_faces = MetaDataType.INT, lambda context: len(context.groups['default']['faces'])
    nr_of_vertices = MetaDataType.INT, lambda context: len(context.vertices)


class MetaDataAssimpTexture(MetaDataExtractor):
    __mimetype__ = 'application/assimp.texture'


class MetaDataAssimpMaterial(MetaDataExtractor):
    __mimetype__ = 'application/assimp.material'


class MetaDataAssimpMesh(MetaDataExtractor):
    __mimetype__ = 'application/assimp.mesh'

    nr_of_faces = MetaDataType.INT, lambda context: len(context.faces)
    nr_of_vertices = MetaDataType.INT, lambda context: len(context.vertices)
    nr_of_normals = MetaDataType.INT, lambda context: len(context.normals)
    nr_of_bones = MetaDataType.INT, lambda context: len(context.bones)
    nr_of_texturecoords = MetaDataType.INT, lambda context: len(context.texturecoords)
    nr_of_anim_meshes = MetaDataType.INT, lambda context: context.numanimmeshes
