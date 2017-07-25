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
        self.tokens = None
        self.output = []
        self.appendToOutput = True

    def next_token(self):
        if self.tokens:
            return self.tokens.pop(0)
        else:
            try:
                line, self.tokens = self.reader.next()
            except StopIteration:
                return None

            if self.appendToOutput:
                self.output.append(line)

            return self.next_token()

    def keysForLevel(self, level):
        currentLevel = level - 1
        expectingKey = False

        token = self.next_token()
        while token:
            if level == currentLevel and expectingKey and token.token_type == TOKEN_IDENTIFIER:
                yield token.associatedValue
                expectingKey = False
                token = self.next_token()
                continue

            if token.token_type == TOKEN_BEGIN_DICTIONARY:
                currentLevel += 1
                expectingKey = True
            elif token.token_type == TOKEN_END_DICTIONARY:
                currentLevel -= 1
            elif token.token_type == TOKEN_SEMICOLON:
                if currentLevel < level:
                    break
                else:
                    expectingKey = True

            token = self.next_token()

    def filterForTokenType(self, tokenType, tokens):
        return filter(lambda token: token.token_type == tokenType, tokens)

    def processKeysForLevel(self, level, additions, subtractions):
        for key in self.keysForLevel(level):
            self.appendToOutput = True

            if key in subtractions:
                if subtractions[key] == None:
                    self.appendToOutput = False
                    del subtractions[key]
                else:
                    self.processKeysForLevel(level+1, additions.get(key, {}), subtractions[key])

            elif key in additions:
                val = additions[key]

                self.processKeysForLevel(level+1, additions[key], {})
                del additions[key]

        # We've passed through all the keys, check if there are still additions as these are values we will have to add
        if additions:
            pass

    def process(self):
        self.processKeysForLevel(1, self.additionDict, self.subtractionDict)
        return ''.join(self.lineBuffer)
