from StringIO import StringIO
from PlistParser import Tokenizer, Token, TOKEN_COMMENT

class PlistLineTokenizer:
    def __init__(self, string_or_stream):
        self.input = string_or_stream
        if type(self.input) in (str, unicode):
            self.input = open(self.input, 'r')

        self.tokenizer = Tokenizer(None)

    def lines(self):
        while True:
            line = self.input.readline()
            if not line:
                break
            yield line

    def tokenizedLines(self):
        for line in self.lines():
            self.tokenizer.input = StringIO(line)
            tokens = PlistTokenLine(list(self.tokenizer.tokenize(ignoring_comments=False))[:-1])
            yield line, tokens

class PlistTokenLine:
    def __init__(self, tokens):
        self.tokens = tuple(tokens)

    def filteredTokens(self):
        return filter(lambda x: x.token_type != TOKEN_COMMENT, self.tokens)

    def __hash__(self):
        return self.filteredTokens().__hash__()

    def __eq__(self, other):
        return type(self) == type(other) and self.filteredTokens() == other.filteredTokens()
