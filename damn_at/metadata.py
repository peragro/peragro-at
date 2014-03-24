from damn_at import MetaDataValue, MetaDataType


class MetaDataExtractor(object):
    @classmethod
    def extract(cls, context):
        metadata = {}
        for field in dir(cls):
            if not field.startswith('__') and field not in ['extract', 'fields']:
                type, func = getattr(cls, field)
                type_name = MetaDataType._VALUES_TO_NAMES[type].lower()+'_value'
                kwargs = {'type': type}
                kwargs[type_name] = func(context)
                metadata[field] = MetaDataValue(**kwargs)
        return metadata

    @classmethod
    def fields(cls):
        return [(field, MetaDataType._VALUES_TO_NAMES[getattr(cls, field)[0]]) for field in dir(cls) if not field.startswith('__') and field not in ['extract', 'fields']]
