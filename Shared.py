#!/usr/bin/env python

from XcodeProject import XcodeProject
from SharedWorkspace import SharedWorkspace
from PlistModifier import PlistModifier
import argparse

if __name__ == "__main__":
    # Command line arguments #####################
    commandLineParser = argparse.ArgumentParser()
    commandLineParser.add_argument("targetProjectDirectory", help="Target project directory")
    commandLineParser.add_argument('-s', '--shared', nargs='+', type=str, help="Shared project directories", required=True)
    commandLineParser.add_argument('-t', '--target', help="Specific target for shared workspace... defaults to the target with the same name as the project if any exists")
    commandLineArgs = commandLineParser.parse_args()
    targetProjectPath = commandLineArgs.targetProjectDirectory
    sharedProjectPaths = commandLineArgs.shared if commandLineArgs.shared else []
    targetToShareInto = commandLineArgs.target
    ##############################################

    targetProject = XcodeProject(targetProjectPath)
    sharedProjectPaths = [XcodeProject(sharedProjectPath) for sharedProjectPath in sharedProjectPaths]

    sharedWorkspace = SharedWorkspace(targetProject, *sharedProjectPaths)
    additionDict, subtractDict = sharedWorkspace.share(targetToShareInto)

    output = PlistModifier(targetProject.plistFilePath).process(additionDict, subtractDict)
    with open(targetProject.plistFilePath, 'w') as file:
        file.write(output)