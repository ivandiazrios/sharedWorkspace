import random
import string
import os

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

def getFullPath(path):
    if os.path.exists(path):
        return path
    elif not os.path.isabs(path):
        # Try to find it under current directory
        cd = os.getcwd()
        fullPath = os.path.join(cd, path)
        if os.path.exists(fullPath):
            return fullPath

    raise ValueError("Could not locate directory %s", path)


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