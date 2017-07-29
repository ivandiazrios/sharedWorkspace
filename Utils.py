import random
import string

def uuid(bits=24):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(bits))

def lazy_property(fn):
    '''Decorator that makes a property lazy-evaluated.
    '''
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property

def stripEnd(text, suffix):
    if not text.endswith(suffix):
        return text
    return text[:len(text)-len(suffix)]

class Lookahead:
    def __init__(self, iter):
        self.iter = iter
        self.buffer = []

    def __iter__(self):
        return self

    def next(self):
        if self.buffer:
            return self.buffer.pop(0)
        else:
            return self.iter.next()

    def peek(self, n=0):
        """Return an item n entries ahead in the iteration."""
        while n >= len(self.buffer):
            try:
                self.buffer.append(self.iter.next())
            except StopIteration:
                return None
        return self.buffer[n]

def itemsWithValueContainingKeyValues(dict, *keyValues):
    allKeyValuesInDict = lambda _, dict: all(dict.get(k, None) == v for k, v in keyValues)
    return filter(allKeyValuesInDict, dict)

def deepDictMerge(source, destination):
    for key, value in source.iteritems():
        if key in destination:
            destinationValue = destination[key]
            if type(destinationValue) == type(value):
                if type(value) == list:
                    destination[key] = value + destinationValue
                elif type(value) == dict:
                    destination[key] = merge(value, destinationValue)
                else:
                    destination[key] = value
            else:
                destination[key] = value
        else:
            destination[key] = value

    return destination