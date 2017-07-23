from PlistLineTokenizer import PlistLineTokenizer
from Utils import Lookahead
from PlistParser import Token, TOKEN_COMMENT
from Utils import appendToEndOfString
import sys
import StringIO

SHARED_WORKSPACE_SIGNATURE = "// Shared workspace tool"

class PlistCombiner:
    def __init__(self, finalPath, targetPath, modifiedPath):
        self.targetInput = targetPath
        self.modifiedInput = modifiedPath
        self.finalOutput = finalPath

        self.debug = False

        if type(self.targetInput) in (str, unicode):
            self.targetInput = open(self.targetInput, 'r')

        if type(self.modifiedInput) in (str, unicode):
            self.modifiedInput = open(self.modifiedInput, 'r')

        self.output = StringIO.StringIO()

    def writeOutput(self):
        if type(self.finalOutput) in (str, unicode):
            if self.debug:
                self.finalOutput = sys.stdout
            else:
                self.finalOutput = open(self.finalOutput, 'w')

        self.finalOutput.write(self.output.getvalue())

    def combine(self):
        targetLineTokenizer = PlistLineTokenizer(self.targetInput)
        modifiedLineTokenizer = PlistLineTokenizer(self.modifiedInput)

        self.targetGen = Lookahead(targetLineTokenizer.tokenizedLines())
        self.modifiedGen = Lookahead(modifiedLineTokenizer.tokenizedLines())

        while True:
            target = self.targetGen.peek()
            modified = self.modifiedGen.peek()

            if target is None and modified is None:
                break
            elif target is None:
                self.output.write(self.modifiedGen.next()[0])
                break
            elif modified is None:
                self.output.write(self.targetGen.next()[0])
                break

            self.step(target, modified)

        self.writeOutput()

    def step(self, target, modified):
        targetLine, targetTokens = target
        modifiedLine, modifiedTokens = modified

        if targetTokens and targetTokens[0].associatedValue and targetTokens[0].associatedValue.startswith("A71DAB0D1E32895B0057C3DD"):
            pass

        if self.debug:
            self.output.write("Target tokens  : " + str(targetTokens) + "\n")
            self.output.write("Modified tokens: " + str(modifiedTokens) + "\n")
            self.output.write("---------------------------------" + "\n")

        if self.isBlankLine(targetTokens) or self.isOnlyComments(targetTokens):
            self.output.write(targetLine)
            self.targetGen.next()

        elif self.tokensAreTheSameWithStrippedComments(targetTokens, modifiedTokens):
            self.output.write(targetLine)
            # Throw away values
            self.targetGen.next()
            self.modifiedGen.next()

        else:
            self.output.write(modifiedLine)
            self.modifiedGen.next()

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


