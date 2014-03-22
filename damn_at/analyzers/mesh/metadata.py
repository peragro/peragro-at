from damn_at.metadata import MetaDataExtractor
from damn_at import MetaDataType
        
    
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
