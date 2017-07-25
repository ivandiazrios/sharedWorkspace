from StringIO import StringIO
from PlistParser import Tokenizer

class PlistLineTokenizer:
    def __init__(self, string_or_stream):
        self.input = string_or_stream
        if type(self.input) in (str, unicode):
            self.input = open(self.input, 'r')

        self.tokenizer = Tokenizer(None)

    def __iter__(self):
        return self

    def next(self):
        line = self.input.readline()

        if not line:
            raise StopIteration()

        self.tokenizer.input = StringIO(line)
        tokens = list(self.tokenizer.tokenize(ignoring_comments=False))[:-1]
        return line, tokens
