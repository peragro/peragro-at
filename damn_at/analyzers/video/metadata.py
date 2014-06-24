from damn_at.metadata import MetaDataExtractor
from damn_at import MetaDataType

class MetaDataExif(MetaDataExtractor):

    duration = MetaDataType.STRING, lambda context : context['duration']
    bit_depth = MetaDataType.INT, lambda context : int(context['bit_depth'])
    width = MetaDataType.INT, lambda context : int(context['image_width'])
    height = MetaDataType.INT, lambda context : int(context['image_height'])
    frame_rate = MetaDataType.STRING, lambda context : context['video_frame_rate']
