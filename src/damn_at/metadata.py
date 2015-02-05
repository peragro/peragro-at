from damn_at import MetaDataValue, MetaDataType


class MetaDataExtractor(object):
    @classmethod
    def extract(cls, context):
        metadata = {}
        for field in dir(cls):
            if not field.startswith('__') and field not in ['extract', 'fields', 'convert']:
                type, func = getattr(cls, field)
                type_name = MetaDataType._VALUES_TO_NAMES[type].lower() + '_value'
                kwargs = {'type': type}
                kwargs[type_name] = func(context)
                if kwargs[type_name] is not None:  # Ignore None values!
                    kwargs[type_name] = cls.convert(type, kwargs[type_name])
                    metadata[field] = MetaDataValue(**kwargs)
        return metadata

    @classmethod
    def convert(cls, type_name, value):
        if type_name == MetaDataType.INT:
            return int(value)
        elif type_name == MetaDataType.DOUBLE:
            return float(value)
        elif type_name == MetaDataType.BOOL:
            return bool(value)
        elif type_name == MetaDataType.STRING:
            return str(value)
        else:
            raise Exception('Unknown type %s' % type_name)

    @classmethod
    def fields(cls):
        return [(field, MetaDataType._VALUES_TO_NAMES[getattr(cls, field)[0]]) for field in dir(cls) if not field.startswith('__') and field not in ['extract', 'fields']]
