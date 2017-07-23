from XcodeProject import XcodeProject
from PlistWriter import PlistWriter
from PlistParser import Parser
from PlistCombiner import PlistCombiner
from SharedWorkspace import SharedWorkspace
import os
import argparse
import StringIO

if __name__ == "__main__":

    # Command line arguments #####################
    commandLineParser = argparse.ArgumentParser()
    commandLineParser.add_argument("project1", help="Path to first project")
    commandLineParser.add_argument("project2", help="Path to second project")
    commandLineArgs = commandLineParser.parse_args()
    targetProjectPath = commandLineArgs.project1
    sharedProjectPath = commandLineArgs.project2
    ##############################################

    targetProject = XcodeProject(targetProjectPath)
    sharedProject = XcodeProject(sharedProjectPath)

    sharedWorkspace = SharedWorkspace(targetProject, sharedProject)
    sharedWorkspace.share()

    modifiedOutputBuffer = StringIO.StringIO()
    PlistWriter(modifiedOutputBuffer).write(sharedWorkspace.outputPlist)
    modifiedOutputBuffer.pos = 0

    with open(targetProject.plistFilePath, 'r') as inputFile:
        inputBuffer = StringIO.StringIO(inputFile.read())

    combiner = PlistCombiner(targetProject.plistFilePath, inputBuffer, modifiedOutputBuffer)
    combiner.combine()
