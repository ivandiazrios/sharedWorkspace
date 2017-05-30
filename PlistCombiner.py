from PlistLineTokenizer import PlistLineTokenizer
from Utils import Lookahead
from PlistParser import Token, TOKEN_COMMENT
from Utils import appendToEndOfString
import sys

SHARED_WORKSPACE_SIGNATURE = "// Shared workspace tool"

class PlistCombiner:
    def __init__(self, finalPath, targetPath, modifiedPath):
        self.targetInput = targetPath
        self.modifiedInput = modifiedPath
        self.output = finalPath

        self.debug = False

        if type(self.targetInput) in (str, unicode):
            self.targetInput = open(self.targetInput, 'r')

        if type(self.modifiedInput) in (str, unicode):
            self.modifiedInput = open(self.modifiedInput, 'r')

        if type(self.output) in (str, unicode):
            if self.debug:
                self.output = sys.stdout
            else:
                self.output = open(self.output, 'w')

    def combine(self):
        targetLineTokenizer = PlistLineTokenizer(self.targetInput)
        modifiedLineTokenizer = PlistLineTokenizer(self.modifiedInput)

        self.targetGen = Lookahead(targetLineTokenizer.tokenizedLines())
        self.modifiedGen = Lookahead(modifiedLineTokenizer.tokenizedLines())

        self.modifiedLinesBuffer = ""

        while True:
            target = self.targetGen.peek()
            modified = self.modifiedGen.peek()

            if target is None and modified is None:
                break

            self.step(target, modified)

    def step(self, target, modified):
        if target is None:
            self.output.write(self.modifiedGen.next()[0])
            return
        elif modified is None:
            self.output.write(self.targetGen.next()[0])
            return

        targetLine, targetTokens = target
        modifiedLine, modifiedTokens = modified

        if self.debug:
            self.output.write("Target tokens  : " + str(targetTokens) + "\n")
            self.output.write("Modified tokens: " + str(modifiedTokens) + "\n")
            self.output.write("---------------------------------" + "\n")

        if self.isBlankLine(targetTokens) or self.isOnlyComments(targetTokens):
            self.clearBuffer()

            self.output.write(targetLine)
            self.targetGen.next()

        elif self.tokensAreTheSameWithStrippedComments(targetTokens, modifiedTokens):
            self.clearBuffer()

            self.output.write(targetLine)
            # Throw away values
            self.targetGen.next()
            self.modifiedGen.next()

        else:
            self.modifiedLinesBuffer += modifiedLine
            self.modifiedGen.next()

    def clearBuffer(self):
        if not self.modifiedLinesBuffer:
            return

        self.output.writelines(appendToEndOfString(self.modifiedLinesBuffer, SHARED_WORKSPACE_SIGNATURE))
        self.modifiedLinesBuffer = ""

    def isOnlyComments(self, targetTokens):
        return all(map(lambda x: type(x) == Token and x.token_type == TOKEN_COMMENT, targetTokens))

    def isBlankLine(self, targetTokens):
        return targetTokens == []

    def tokensAreTheSameWithStrippedComments(self, targetTokens, modifiedTokens):
        return self.stripCommentTokens(targetTokens) == self.stripCommentTokens(modifiedTokens)

    def stripCommentTokens(self, tokens):
        return filter(lambda x: type(x) == Token and x.token_type != TOKEN_COMMENT, tokens)

    def annotateLineWithToolSignature(self, line):
        return appendToEndOfString(line, SHARED_WORKSPACE_SIGNATURE)


