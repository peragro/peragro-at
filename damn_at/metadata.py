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
                if kwargs[type_name] is not None: # Ignore None values!
                    kwargs[type_name] = cls.convert(type, kwargs[type_name])
                    metadata[field] = MetaDataValue(**kwargs)
        return metadata

    @classmethod
    def convert(cls, type, value):
        if type == MetaDataType.INT:
            return int(value)
        elif type == MetaDataType.DOUBLE:
            return float(value)
        elif type == MetaDataType.BOOL:
            return bool(value)
        elif type == MetaDataType.STRING:
            return str(value)
        else:
            raise Exception('Unknown type %s'%(type_name))

    @classmethod
    def fields(cls):
        return [(field, MetaDataType._VALUES_TO_NAMES[getattr(cls, field)[0]]) for field in dir(cls) if not field.startswith('__') and field not in ['extract', 'fields']]
