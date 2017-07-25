from Utils import Lookahead
from PlistParser import *
from PlistLineTokenizer import PlistLineTokenizer
from Writer import Writer

class PlistModifier:
    def __init__(self, string_or_stream, additionDict, subtractionDict):
        self.input = string_or_stream
        if type(self.input) in (str, unicode):
            self.input = open(self.input, 'r')

        self.reader = Lookahead(PlistLineTokenizer(self.input))
        self.additionDict = additionDict
        self.subtractionDict = subtractionDict
        self.tokens = None
        self.line = None
        self.output = []
        self.appendToOutput = True
        self.indentLevel = 0
        self.plistWriter = Writer()

    def next_token(self):
        if self.tokens:
            return self.tokens.pop(0)
        else:
            if self.appendToOutput and self.line:
                self.output.append(self.line)
            try:
                self.line, self.tokens = self.reader.next()
            except StopIteration:
                return None

            return self.next_token()

    def filterForTokenType(self, tokenType, tokens):
        return filter(lambda token: token.token_type == tokenType, tokens)

    def process(self):
        self.processValue(self.additionDict, self.subtractionDict)
        self.output += self.line
        return ''.join(self.output)

    def processValue(self, additions, deletions):
        token = self.next_token()
        while token:
            if token.token_type == TOKEN_BEGIN_DICTIONARY:
                self.indentLevel += 1
                self.processDictionary(additions, deletions)
                self.indentLevel -= 1
                return
            elif token.token_type == TOKEN_BEGIN_LIST:
                self.indentLevel += 1
                self.processList(additions, deletions)
                self.indentLevel -= 1
                return

            token = self.next_token()

    def processDictionary(self, additions, subtractions):
        for key in self.keysForLevel():
            self.appendToOutput = True

            needToSubtractKey = False
            needToAddKey = False

            if subtractions and key in subtractions:
                if subtractions[key] == None:
                    self.appendToOutput = False
                    del subtractions[key]
                    continue

                needToSubtractKey = True

            if additions and key in additions:
                needToAddKey = True

            additionsToProcess = additions[key] if needToAddKey else None
            subtractionsToProcess = subtractions[key] if needToSubtractKey else None

            if additionsToProcess:
                del additions[key]

            if additionsToProcess or subtractionsToProcess:
                self.processValue(additionsToProcess, subtractionsToProcess)

        self.appendToOutput = True

        if additions:
            for k,v in additions.iteritems():
                self.output.append(self.plistWriter.writeKeyValue(k, v, initial_indent=self.indentLevel))

    def processList(self, additions, subtractions):
        assert type(additions) == list or additions is None
        assert type(subtractions) == list or subtractions is None

        for item in self.itemsForLevel():

            # Write new items at beginning of list
            if additions:
                self.output.append(self.plistWriter.writeListItems(additions, initial_indent=self.indentLevel))
                additions = None

            self.appendToOutput = True

            if subtractions and item in subtractions:
                self.appendToOutput = False

        self.appendToOutput = True

    def itemsForLevel(self):
        currentLevel = 1
        expectingItem = True

        token = self.next_token()
        while token:
            if currentLevel == 1 and expectingItem:
                # We don't have a need for other values but identifiers and strings in lists
                if token.token_type in [TOKEN_IDENTIFIER, TOKEN_STRING]:
                    yield token.associatedValue
                    expectingItem = False
                    token = self.next_token()

            if token.token_type == TOKEN_BEGIN_LIST:
                currentLevel += 1
                expectingItem = True
            elif token.token_type == TOKEN_END_LIST:
                currentLevel -= 1
                if not currentLevel:
                    break
            elif token.token_type == TOKEN_COMMA:
                expectingItem = True

            token = self.next_token()

    def keysForLevel(self):
        currentLevel = 1
        expectingKey = True

        token = self.next_token()
        while token:
            if currentLevel == 1 and expectingKey and token.token_type == TOKEN_IDENTIFIER:
                yield token.associatedValue
                expectingKey = False
                token = self.next_token()
                continue

            if token.token_type == TOKEN_BEGIN_DICTIONARY:
                currentLevel += 1
                expectingKey = True
            elif token.token_type == TOKEN_END_DICTIONARY:
                currentLevel -= 1
                if not currentLevel:
                    break
            elif token.token_type == TOKEN_SEMICOLON:
                expectingKey = True

            token = self.next_token()
