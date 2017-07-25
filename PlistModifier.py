from Utils import Lookahead
from PlistParser import *
from PlistLineTokenizer import PlistLineTokenizer

class PlistModifier:
    def __init__(self, string_or_stream, additionDict, subtractionDict):
        self.input = string_or_stream
        if type(self.input) in (str, unicode):
            self.input = open(self.input, 'r')

        self.reader = Lookahead(PlistLineTokenizer(self.input))
        self.additionDict = additionDict
        self.subtractionDict = subtractionDict


        self.output = []
        self.currentKey = None
        self.keyStack = []
        self.current = None

    def tokens(self):
        self.lineBuffer = []

        for line, tokens in self.reader:
            for token in tokens:
                yield token
            self.lineBuffer.append(line)

    def keys(self, level):
        self.currentKeyLevel = 0
        self.leavingKeyLevel = False

        expectingKey = False

        for token in self.tokens():
            if self.keyLevel == self.currentKeyLevel and expectingKey and token.token_type == TOKEN_IDENTIFIER:
                yield token.associatedValue
                expectingKey = False
                continue

            if token.token_type == TOKEN_BEGIN_DICTIONARY:
                self.currentKeyLevel += 1
                expectingKey = True
            elif token.token_type == TOKEN_SEMICOLON:
                expectingKey = True
            elif token.token_type == TOKEN_END_DICTIONARY:
                self.currentKeyLevel -= 1
                self.leavingKeyLevel = True

    def filterForTokenType(self, tokenType, tokens):
        return filter(lambda token: token.token_type == tokenType, tokens)

    def processKeysForLevel(self, level):


    # def enterPlist(self):
    #     for line, tokens in self.reader:
    #         self.output.append(line)
    #         if self.filterComments(tokens) == [Token(TOKEN_BEGIN_DICTIONARY, None)]:
    #             return

    def process(self):
        self.keyLevel = 1

        for key in self.keys():
            self.output += self.lineBuffer




