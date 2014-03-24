"""
Options
"""
import os
import sys
from string import Template

from damn_at import mimetypes
from damn_at import utilities

class Sizes():
    try:
        maxint = sys.maxint
    except:
        maxint = sys.maxsize


class OptionException(Exception):
    """Base Option Exception"""
    def __init__(self, msg):
        Exception.__init__(self)
        self.msg = msg
    def __str__(self):
        return repr(self.msg)


class OptionParseException(OptionException):
    """Something wrong with the option's format"""
    pass
 

class OptionConstraintException(OptionException):
    """Value did not comply with the constraints"""
    pass

    
class BaseOption(object):
    """BaseOption"""
    def __init__(self, name, description, default):
        self.name = name
        self.description = description
        self.default = default
        self.is_array = False
        
    def parse_from_string(self, a_string):    
        raise NotImplementedError("'parse_from_string' must be reimplemented by %s" % self)
        
    def type_description(self):
        raise NotImplementedError("'type_description' must be reimplemented by %s" % self)
        
    def constraint_description(self):    
        raise NotImplementedError("'constraint_description' must be reimplemented by %s" % self)
        
    def default_description(self):
        raise NotImplementedError("'default_description' must be reimplemented by %s" % self)
        
        
class VectorOption(BaseOption):
    """Base class for vector options"""
    def __init__(self, type, name, description, default, min, max, size):
        BaseOption.__init__(self, name, description, default)
        self.type = type
        self.size = size
        self.min = min
        self.max = max
        
    def _clean(self, a_string):
        if a_string.startswith('('):
            a_string = a_string[1:]
        if a_string.startswith(')'):
            a_string = a_string[:-1]
        return a_string
        
    def parse_from_string(self, a_string):
        splits = self._clean(a_string).split(',')
        if self.size and len(splits)!=self.size:
            raise OptionParseException('%s not of size %d!'%(a_string, self.size))
        return_value = []
        for i, val in enumerate(splits):
            value = self.type(val) #Todo:catch
            if value != self.default[i]:
                if value < self.min or value > self.max:
                    raise OptionConstraintException('%d < %d < %d failed!' % (self.min, value, self.max))
            return_value.append(value)
        if self.size==1:
            return return_value[0]
        return return_value

    @property
    def type_description(self):
        if self.size:
            size = self.size if self.size > 1 else ''
        else:
            size = '*'
        return '%s%s' % (self.type.__name__, size)

    @property        
    def constraint_description(self):
        return 'Value needs to be between %s and %s' % (self.min, self.max)

    @property
    def default_description(self):
        try:
            iterator = map(lambda x: str(x), iter(self.default))
            return ','.join(iterator)
        except TypeError as e:
            # not iterable
            return str(self.default)
            


class IntVectorOption(VectorOption):
    def __init__(self, name="", description="", default=(0, 0, 0), min=-Sizes.maxint, max=Sizes.maxint, size=3):
        VectorOption.__init__(self, type=int, name=name, description=description, default=default, min=min, max=max, size=size)

class FloatOption(VectorOption):
    def __init__(self, name="", description="", default=0.0, min=sys.float_info.min, max=sys.float_info.max):
        VectorOption.__init__(self, type=float, name=name, description=description, default=default, min=min, max=max, size=1)

class FloatArrayOption(VectorOption):
    def __init__(self, name="", description="", default=0.0, min=sys.float_info.min, max=sys.float_info.max):
        VectorOption.__init__(self, type=float, name=name, description=description, default=default, min=min, max=max, size=None)
        self.is_array = True


class EnumOption(BaseOption):
    """Class for enum options"""
    def __init__(self, name, description, choices, default):
        BaseOption.__init__(self, name, description, default)
        self.choices = choices
        
    def parse_from_string(self, a_string):
        if a_string not in self.choices:
            raise OptionConstraintException('%s not in %s' % (a_string, str(self.choices)))
        return a_string

    @property
    def type_description(self):
        return 'enum'

    @property        
    def constraint_description(self):
        return 'Value needs to be one of %s' % (str(self.choices))

    @property
    def default_description(self):
        return str(self.default)        


def options_to_template(options):
    path = ''
    for option in options:
        path = os.path.join(path, '${'+str(option.name)+'}')
    return os.path.join('assets', '${uuid}', '${dstFormat}', path, '${uuid}${extension}')

    
def parse_options(convert_map_entry, **options):
    opts = {}
    entries = dict([(option.name, option) for option in convert_map_entry])
    for name, option in entries.items():
        if name in options:
            opts[name] = entries[name].parse_from_string(options[name])
        else:
            opts[name] = entries[name].default
    return opts


def parse_options2(convert_map_entry, **options): #TODO: remove
    opts = {}
    entries = dict([(option.name, option) for option in convert_map_entry])
    for name, value in options.items():
        if name in entries:
            if value != entries[name].default_description:
                opts[name] = entries[name].parse_from_string(value)
            else:
                opts[name] = entries[name].default
    return opts

def expand_path_template(template, mimetype, asset_id, **options):
    t = Template(template)
    uuid = utilities.unique_asset_id_reference(asset_id)
    return t.safe_substitute(uuid=uuid, dstFormat=mimetype, extension=str(mimetypes.guess_extension(mimetype)), **options)
