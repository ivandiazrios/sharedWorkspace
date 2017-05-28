from PlistLineTokenizer import PlistLineTokenizer
from Utils import Lookahead

class PlistCombiner:
    def __init__(self, finalPath, targetPath, modifiedPath):
        self.targetInput = targetPath
        self.modifiedInput = modifiedPath
        self.output = finalPath

        if type(self.targetInput) in (str, unicode):
            self.targetInput = open(self.targetInput, 'r')

        if type(self.modifiedInput) in (str, unicode):
            self.modifiedInput = open(self.modifiedInput, 'r')

        if type(self.output) in (str, unicode):
            self.output = open(self.output, 'w')

    def combine(self):
        targetLineTokenizer = PlistLineTokenizer(self.targetInput)
        modifiedLineTokenizer = PlistLineTokenizer(self.modifiedInput)

        targetGen = Lookahead(targetLineTokenizer.tokenizedLines())
        modifiedGen = Lookahead(modifiedLineTokenizer.tokenizedLines())

        while True:
            target = targetGen.peek()
            modified = modifiedGen.peek()

            shouldPrintTarget = self.shouldPrintTarget(target, modified)

            if shouldPrintTarget is None:
                break
            elif shouldPrintTarget:
                print targetGen.next()[0]
            else:
                print modifiedGen.next()[0]

    def shouldPrintTarget(self, target, modified):
        if target is None and modified is None:
            return None
        if target is None:
            return False
        elif modified is None:
            return True

        return True
