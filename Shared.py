#!/usr/bin/env python
import argparse
from PlistModifier import PlistModifier
from SharedWorkspace import SharedWorkspace
from XcodeProject import XcodeProject

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

    if additionDict or subtractDict:
        plistModifier = PlistModifier(targetProject.plistFilePath)
        try:
            output = plistModifier.process(additionDict, subtractDict)
        except:
            print "Error: Unable to modify existing project file"
        else:
            with open(targetProject.plistFilePath, 'w') as file:
                file.write(output)
