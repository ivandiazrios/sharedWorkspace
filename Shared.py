#!/usr/bin/env python

from XcodeProject import XcodeProject
from SharedWorkspace import SharedWorkspace
from PlistModifier import PlistModifier
import argparse

if __name__ == "__main__":
    # Command line arguments #####################
    commandLineParser = argparse.ArgumentParser()
    commandLineParser.add_argument("targetProjectPath", help="Path to first project")
    commandLineParser.add_argument('-s', '--shared', nargs='+', type=str)
    commandLineArgs = commandLineParser.parse_args()
    targetProjectPath = commandLineArgs.targetProjectPath
    sharedProjectPaths = commandLineArgs.shared
    ##############################################

    targetProject = XcodeProject(targetProjectPath)
    sharedProjectPaths = [XcodeProject(sharedProjectPath) for sharedProjectPath in sharedProjectPaths]

    sharedWorkspace = SharedWorkspace(targetProject, *sharedProjectPaths)
    additionDict, subtractDict = sharedWorkspace.share()

    output = PlistModifier(targetProject.plistFilePath).process(additionDict, subtractDict)
    with open(targetProject.plistFilePath, 'w') as file:
        file.write(output)