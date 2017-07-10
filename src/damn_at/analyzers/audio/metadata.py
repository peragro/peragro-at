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


class MetaDataFeatureExtraction(MetaDataExtractor):

    bpm = MetaDataType.DOUBLE, lambda context: float(context['bpm'])
    beats_count = MetaDataType.DOUBLE, lambda context: float(context['beats_count'])
    chord = MetaDataType.STRING, lambda context: context['chord']
    key = MetaDataType.STRING, lambda context: context['key']
    average_loudness = MetaDataType.DOUBLE, lambda context: float(context['average_loudness'])
    lossless = MetaDataType.BOOL, lambda context: bool(context['lossless'])
    mood_party = MetaDataType.STRING, lambda context: context['mood_party']
    genre_electronic = MetaDataType.STRING, lambda context: context['genre_electronic']
    voice_instrumental = MetaDataType.STRING, lambda context: context['voice_instrumental']
    mood_aggressive = MetaDataType.STRING, lambda context: context['mood_aggressive']
    ismir04_rhythm = MetaDataType.STRING, lambda context: context['ismir04_rhythm']
    mood_electronic = MetaDataType.STRING, lambda context: context['mood_electronic']
    timbre = MetaDataType.STRING, lambda context: context['timbre']
    danceability = MetaDataType.STRING, lambda context: context['danceability']
    genre_rosamerica = MetaDataType.STRING, lambda context: context['genre_rosamerica']
    mood_relaxed = MetaDataType.STRING, lambda context: context['mood_relaxed']
    mood_acoustic = MetaDataType.STRING, lambda context: context['mood_acoustic']
    moods_mirex = MetaDataType.STRING, lambda context: context['moods_mirex']
    mood_happy = MetaDataType.STRING, lambda context: context['mood_happy']
    genre_tzanetakis = MetaDataType.STRING, lambda context: context['genre_tzanetakis']
    genre_dortmund = MetaDataType.STRING, lambda context: context['genre_dortmund']
    mood_sad = MetaDataType.STRING, lambda context: context['mood_sad']
    gender = MetaDataType.STRING, lambda context: context['gender']
    tonal_atonal = MetaDataType.STRING, lambda context: context['tonal_atonal']