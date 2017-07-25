from PlistParser import *
from PlistLineTokenizer import PlistLineTokenizer
from Writer import Writer
from StringIO import StringIO

class PlistModifier:
    def __init__(self, string_or_stream):
        self.input = string_or_stream
        if type(self.input) in (str, unicode):
            self.input = open(self.input, 'r')

        self.output = StringIO()
        self.lineBuffer = StringIO()
        self.shouldWrite = True
        self.writeToBuffer = False
        self.reader = PlistLineTokenizer(self.input)
        self.line, self.tokens = [], []
        self.indentLevel = 0
        self.writer = Writer()

    def next_token(self):
        if self.tokens:
            return self.tokens.pop(0)
        else:
            if self.line and self.shouldWrite and not self.writeToBuffer:
                self.output.write(self.line)
            elif self.line and self.writeToBuffer:
                self.lineBuffer.write(self.line)

            try:
                self.line, self.tokens = self.reader.next()
            except StopIteration:
                return None

            return self.next_token()

    # Helper methods
    def removeLastOccurenceFromList(self, l, element):
        if element in l:
            l.reverse()
            l.remove(element)
            l.reverse()

    def getParsedItemFromItem(self, item):
        item.pos = 0
        tokens = list(Tokenizer(item).tokenize())
        self.removeLastOccurenceFromList(tokens, Token(TOKEN_COMMA, None))
        parser = Parser(None)
        parser.tokenizer = iter(tokens)
        return parser.parse()

    def addKeyValuesFromDict(self, dict):
        for k, v in dict.iteritems():
            self.output.write(self.writer.writeKeyValue(k, v, initial_indent=self.indentLevel))

    def saveCurrentLine(self):
        self.output.write(self.line)
        self.line = None

    def addNewItemsToList(self, items):
        self.saveCurrentLine()
        self.output.write(self.writer.writeListItems(items, initial_indent=self.indentLevel))

    def shouldDeleteKey(self, key, subtractionDict):
        return subtractionDict and key in subtractionDict and subtractionDict[key] == None

    def modifiedDictForKey(self, key, additionDict, subtractionDict):
        keyAddictionDict = None
        keySubtractionDict = None

        if additionDict and key in additionDict:
            keyAddictionDict = additionDict[key]
        if subtractionDict and key in subtractionDict:
            keySubtractionDict = subtractionDict[key]

        return keyAddictionDict, keySubtractionDict

    def clearBuffer(self):
        self.lineBuffer = StringIO()

    def saveBuffer(self):
        self.output.write(self.lineBuffer.getvalue())
        self.lineBuffer = StringIO()

    # Process methods
    def process(self, additionDict, subtractionDict):
        self.processValue(additionDict, subtractionDict)
        self.saveCurrentLine()
        return self.output.getvalue()

    def processValue(self, additionDict, subtractionDict):
        token = self.next_token()
        # While loop to skip comments
        while token:
            if token.token_type == TOKEN_BEGIN_DICTIONARY:
                self.indentLevel += 1
                self.processDict(additionDict, subtractionDict)
                self.indentLevel -= 1
                return
            elif token.token_type == TOKEN_BEGIN_LIST:
                self.indentLevel += 1
                self.processBasicList(additionDict, subtractionDict)
                self.indentLevel -= 1
                return

            token = self.next_token()

    # Process dictionary methods
    def processDict(self, additionDict, subtractionDict):
        for key in self.dictKeys():
            self.shouldWrite = True

            if self.shouldDeleteKey(key, subtractionDict):
                self.shouldWrite = False
                del subtractionDict[key]

            keyAdditionDict, keySubtractionDict = self.modifiedDictForKey(key, additionDict, subtractionDict)

            if keyAdditionDict:
                del additionDict[key]

            if keySubtractionDict:
                del subtractionDict[key]

            if keyAdditionDict or keySubtractionDict:
                self.processValue(keyAdditionDict, keySubtractionDict)

        if additionDict:
            self.addKeyValuesFromDict(additionDict)
            additionDict.clear()

        self.shouldWrite = True

    def dictKeys(self):
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

    # Process list methods
    def processList(self, additionItems, subtractionItems):
        if additionItems:
            self.addNewItemsToList(additionItems)
            del additionItems[:]

        self.saveCurrentLine()
        self.writeToBuffer = True

        for item in self.getListItems():
            # Item will be the string sat in the line buffer which we need to parse, it will also end in a comma
            item = self.getParsedItemFromItem(item)
            if subtractionItems and item in subtractionItems:
                self.clearBuffer()
                subtractionItems.remove(item)
            else:
                self.saveBuffer()

        self.writeToBuffer = False

    def processBasicList(self, additions, subtractions):
        # Write new items at beginning of list
        if additions:
            self.addNewItemsToList(additions)
            del additions[:]

        for item in self.getBasicListItems():
            self.shouldWrite = True

            if subtractions and item in subtractions:
                self.shouldWrite = False

        self.shouldWrite = True

    def getListItems(self):
        currentLevel = 1
        hasPriorItem = False

        token = self.next_token()
        while token:
            if currentLevel == 1 and hasPriorItem:
                yield self.lineBuffer
                hasPriorItem = False
                continue

            if token.token_type == TOKEN_BEGIN_LIST:
                currentLevel += 1
            elif token.token_type == TOKEN_END_LIST:
                currentLevel -= 1
                if not currentLevel:
                    if self.lineBuffer.getvalue():
                        yield self.lineBuffer
                    break
            elif token.token_type == TOKEN_COMMA:
                hasPriorItem = True

            token = self.next_token()

    def getBasicListItems(self):
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