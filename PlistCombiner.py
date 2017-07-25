from PlistLineTokenizer import PlistLineTokenizer, PlistTokenLine
from Utils import Lookahead
from PlistParser import Token, TOKEN_COMMENT
from Utils import appendToEndOfString
import sys
import StringIO
import difflib

SPACE_OR_COMMENT_PLIST_TOKENLINE = PlistTokenLine([])

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

        targetLines, targetTokens = map(list, zip(*targetLineTokenizer.tokenizedLines()))
        modifiedLines, modifiedTokens = map(list, zip(*modifiedLineTokenizer.tokenizedLines()))

        matcher = difflib.SequenceMatcher(None, targetTokens, modifiedTokens)
        for n, (tag, i1, i2, j1, j2) in enumerate(reversed(matcher.get_opcodes())):

            if tag == 'delete':
                for indexToDelete in reversed(range(i1, i2)):
                    if targetTokens[indexToDelete] == SPACE_OR_COMMENT_PLIST_TOKENLINE:
                        continue
                    else:
                        del targetLines[indexToDelete]

            elif tag == 'insert':
                targetLines[i1:i2] = modifiedLines[j1:j2]

            elif tag == 'replace':
                # Only replace the lines if they contain something besides empty lines or lines with only comments
                # If not just add the replacement lines after the comment/empty lines.
                print "Replace..."
                print ''.join(targetLines[i1:i2])
                print "With..."
                print ''.join(modifiedLines[j1:j2])

                targetLines[i1:i2] = modifiedLines[j1:j2]
                continue

                x = targetTokens[i1:i2]
                y = filter(lambda x: x != SPACE_OR_COMMENT_PLIST_TOKENLINE, targetTokens[i1:i2])
                if any(filter(lambda x: x != SPACE_OR_COMMENT_PLIST_TOKENLINE, targetTokens[i1:i2])):
                    targetLines[i1:i2] = modifiedLines[j1:j2]
                else:
                    targetLines[i1:i1] = modifiedLines[j1:j2]

        self.output = StringIO.StringIO(''.join(targetLines))
        self.writeOutput()

