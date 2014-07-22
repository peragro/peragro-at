from damn_at.metadata import MetaDataExtractor
from damn_at import MetaDataType

class MetaDataPNG(MetaDataExtractor):
    __mimetype__ = 'image/png'

    width = MetaDataType.INT, lambda context :int(context['image_width'])
    height = MetaDataType.INT, lambda context :int(context['image_height'])
    bit_depth = MetaDataType.INT, lambda context : int(context['bit_depth'])
    color_type = MetaDataType.STRING, lambda context : context['color_type']
    compression = MetaDataType.STRING, lambda context : context['compression']
    interlace = MetaDataType.STRING, lambda context : context['interlace']
    filter = MetaDataType.STRING, lambda context : context['filter']
    srgb_rendering = MetaDataType.STRING, lambda context :context.get('srgb_rendering', '')

class MetaDataJPG(MetaDataExtractor):
    __mimetype__ = 'image/jpeg'

    width = MetaDataType.INT, lambda context :int(context['image_width'])
    height = MetaDataType.INT, lambda context :int(context['image_height'])
    encoding_process = MetaDataType.STRING, lambda context :context['encoding_process']
    bits_per_sample = MetaDataType.INT, lambda context:int(context['bits_per_sample'])
    color_components = MetaDataType.INT, lambda context:int(context['color_components'])

class MetaDataBMP(MetaDataExtractor):
    __mimetype__ = 'image/x-ms-bmp'

    width = MetaDataType.INT, lambda context :int(context['image_width'])
    height = MetaDataType.INT, lambda context :int(context['image_height'])
    bit_depth = MetaDataType.INT, lambda context : int(context['bit_depth'])
    compression = MetaDataType.STRING, lambda context : context['compression']
    planes = MetaDataType.INT, lambda context :int(context['planes'])

class MetaDataPSD(MetaDataExtractor):
    __mimetype__ = 'image/x-photoshop'

    width = MetaDataType.INT, lambda context :int(context['image_width'])
    height = MetaDataType.INT, lambda context :int(context['image_height'])
    bit_depth = MetaDataType.INT, lambda context : int(context['bit_depth'])
    creator_tool = MetaDataType.STRING, lambda context : context['creator_tool']
    color_mode = MetaDataType.STRING, lambda context : context['color_mode']
