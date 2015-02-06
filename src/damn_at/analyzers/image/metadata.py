from damn_at.metadata import MetaDataExtractor
from damn_at import MetaDataType


class MetaDataPNG(MetaDataExtractor):
    __mimetype__ = 'image/png'

    width = MetaDataType.INT, lambda context: context.get('image_width', None)
    height = MetaDataType.INT, lambda context: context.get('image_height', None)
    bit_depth = MetaDataType.INT, lambda context: context.get('bit_depth', None)
    color_type = MetaDataType.STRING, lambda context: context.get('color_type', None)
    compression = MetaDataType.STRING, lambda context: context.get('compression', None)
    interlace = MetaDataType.STRING, lambda context: context.get('interlace', None)
    filter = MetaDataType.STRING, lambda context: context.get('filter', None)
    srgb_rendering = MetaDataType.STRING, lambda context: context.get('srgb_rendering', '')


class MetaDataJPG(MetaDataExtractor):
    __mimetype__ = 'image/jpeg'

    width = MetaDataType.INT, lambda context: context.get('image_width', None)
    height = MetaDataType.INT, lambda context: context.get('image_height', None)
    encoding_process = MetaDataType.STRING, lambda context: context.get('encoding_process', None)
    bits_per_sample = MetaDataType.INT, lambda context: context.get('bits_per_sample', None)
    color_components = MetaDataType.INT, lambda context: context.get('color_components', None)


class MetaDataBMP(MetaDataExtractor):
    __mimetype__ = 'image/x-ms-bmp'

    width = MetaDataType.INT, lambda context: context.get('image_width', None)
    height = MetaDataType.INT, lambda context: context.get('image_height', None)
    bit_depth = MetaDataType.INT, lambda context: context.get('bit_depth', None)
    compression = MetaDataType.STRING, lambda context: context.get('compression', None)
    planes = MetaDataType.INT, lambda context: context.get('planes', None)


class MetaDataPSD(MetaDataExtractor):
    __mimetype__ = 'image/x-photoshop'

    width = MetaDataType.INT, lambda context: context.get('image_width', None)
    height = MetaDataType.INT, lambda context: context.get('image_height', None)
    bit_depth = MetaDataType.INT, lambda context: context.get('bit_depth', None)
    creator_tool = MetaDataType.STRING, lambda context: context.get('creator_tool', None)
    color_mode = MetaDataType.STRING, lambda context: context.get('color_mode', None)


class MetaDataXCF(MetaDataExtractor):
    __mimetype__ = 'application/x-xcf'

    width = MetaDataType.INT, lambda context: context.get('image_width', None)
    height = MetaDataType.INT, lambda context: context.get('image_height', None)
    compression = MetaDataType.STRING, lambda context: context.get('compression', None)
    color_mode = MetaDataType.STRING, lambda context: context.get('color_mode', None)


class MetaDataTGA(MetaDataExtractor):
    __mimetype__ = 'image/tga'

    width = MetaDataType.INT, lambda context: context.get('size', [None])[0]
    height = MetaDataType.INT, lambda context: context.get('size', [None, None])[1]
    format = MetaDataType.STRING, lambda context: context.get('format', None)
    color_mode = MetaDataType.STRING, lambda context: context.get('mode', None)
    orientation = MetaDataType.INT, lambda context: context.get('orientation', None)
