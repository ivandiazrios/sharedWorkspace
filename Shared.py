#!/usr/bin/env python
import argparse
from PlistModifier import PlistModifier
from SharedWorkspace import SharedWorkspace
from XcodeProject import XcodeProject
import os

if __name__ == "__main__":
    # Command line arguments #####################
    commandLineParser = argparse.ArgumentParser()
    commandLineParser.add_argument("targetProjectDirectory", help="Target project directory")
    commandLineParser.add_argument('-s', '--shared', nargs='+', type=str, help="Shared project directories", required=True)
    commandLineParser.add_argument('-t', '--target', help="Specific target for shared workspace... defaults to the target with the same name as the project if any exists")
    commandLineArgs = commandLineParser.parse_args()
    pathOfTargetProject = commandLineArgs.targetProjectDirectory
    pathOfSharedProjects = commandLineArgs.shared if commandLineArgs.shared else []
    target = commandLineArgs.target
    ##############################################

    pathOfTargetProject, pathOfSharedProjects = os.path.abspath(pathOfTargetProject), map(os.path.abspath, pathOfSharedProjects)

    targetProject = XcodeProject(pathOfTargetProject)
    sharedProjectPaths = [XcodeProject(sharedProjectPath) for sharedProjectPath in pathOfSharedProjects]

    sharedWorkspace = SharedWorkspace(targetProject, *sharedProjectPaths)
    additionDict, subtractDict = sharedWorkspace.share(target)

    if additionDict or subtractDict:
        try:
            plistModifier = PlistModifier(targetProject.plistFilePath)
            output = plistModifier.process(additionDict, subtractDict)
        except:
            print "Error: Unable to modify existing project file"
        else:
            with open(targetProject.plistFilePath, 'w') as file:
                file.write(output)
