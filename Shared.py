from XcodeProject import XcodeProject
from SharedWorkspace import SharedWorkspace
from PlistModifier import PlistModifier
import argparse

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
    additionDict, subtractDict = sharedWorkspace.share()

    output = PlistModifier(targetProject.plistFilePath, additionDict, subtractDict).process()
    with open(targetProject.plistFilePath, 'w') as file:
        file.write(output)