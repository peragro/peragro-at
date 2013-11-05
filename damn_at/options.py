"""
Options
"""
import os
import sys

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
        
    def parse_from_string(self, a_string):
        splits = a_string.split(',')
        if len(splits)!=self.size:
            raise OptionParseException('%s not of size %d!'%(a_string, self.size))
        return_value = []
        for val in splits:
            value = self.type(a_string) #Todo:catch
            if value < self.min or value > self.max:
                raise OptionConstraintException('%d < %d < %d failed!' % (self.min, value, self.max))
            return_value.append(value)
        return return_value

    @property
    def type_description(self):
        return '%s%s' % (self.type.__name__, self.size if self.size > 1 else '')

    @property        
    def constraint_description(self):
        return 'Value needs to be between %s and %s' % (self.min, self.max)

    @property
    def default_description(self):
        return str(self.default)


class IntVectorOption(VectorOption):
    def __init__(self, name="", description="", default=(0, 0, 0), min=-sys.maxint, max=sys.maxint, size=3):
        VectorOption.__init__(self, type=int, name=name, description=description, default=default, min=min, max=max, size=size)

class FloatOption(VectorOption):
    def __init__(self, name="", description="", default=0.0, min=sys.float_info.min, max=sys.float_info.max):
        VectorOption.__init__(self, type=float, name=name, description=description, default=default, min=min, max=max, size=1)

        
def options_to_template(options):
    path = ''
    for option in options:
        path = os.path.join(path, '${'+str(option.name)+'}')
    return os.path.join('assets', '${uuid}', '${dstFormat}', path, '${uuid}${extension}')
    
