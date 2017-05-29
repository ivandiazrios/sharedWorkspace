import random
import string

def tabsToSpaces(string, tab_space=4):
    return string.replace('\t', tab_space*' ')

def appendToEndOfString(string, string_to_append):
    endInNewline = False
    if string[-1] == '\n':
        endInNewline = True
        string = string[:-1]

    lines = tabsToSpaces(string).split('\n')
    max_line_length = max([len(line) for line in lines])
    pad_formatter = "{:%s}" % (max_line_length + 1)
    output = '\n'.join([pad_formatter.format(line) + string_to_append for line in lines])
    if endInNewline:
        output += '\n'
    return output

def uuid(bits=24):
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(bits))

class Stack:
    def __init__(self):
        self.__storage = []

    def isEmpty(self):
        return len(self.__storage) == 0

    def push(self,p):
        self.__storage.append(p)

    def pop(self):
        return self.__storage.pop()

    def peek(self):
        return self.__storage[-1]

    def __repr__(self):
        return self.__storage.__repr__()

    def __iter__(self):
        return iter(self.__storage)

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