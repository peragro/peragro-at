from damn_at.metadata import MetaDataExtractor
from damn_at import MetaDataType


class MetaDataSox(MetaDataExtractor):

    duration = MetaDataType.STRING, lambda context: context['duration']
    precision = MetaDataType.STRING, lambda context: context['precision']
    bit_rate = MetaDataType.STRING, lambda context: context['bit_rate']
    channels = MetaDataType.INT, lambda context: int(context['channels'])
    sample_rate = MetaDataType.INT, lambda context: int(context['sample_rate'])


class MetaDataAcoustID(MetaDataExtractor):

    duration = MetaDataType.STRING, lambda context: context['duration']
    fingerprint = MetaDataType.STRING, lambda context: context['fingerprint']
    fingerprint_uuid = MetaDataType.STRING, lambda context: context['fingerprint_uuid']
