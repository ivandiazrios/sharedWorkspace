from XcodeProject import XcodeProject
from PlistWriter import PlistWriter
from PlistCombiner import PlistCombiner
from Utils import appendToEndOfString
import os

PROJECT1_PATH = "/Users/Ivan/Desktop/Test/Test"
PROJECT2_PATH = "/Users/Ivan/Desktop/Projects/Test2"
PROJECT_OUTPUT_PATH = "/Users/Ivan/Desktop/Test/Test.xcodeproj/project.pbxproj"

if __name__ == "__main__":
    targetProject = XcodeProject(PROJECT1_PATH)
    sharedProject = XcodeProject(PROJECT2_PATH)

    modifiedPlistPath = targetProject.plistFilePath + "tmp"
    combinedPlistPath = targetProject.plistFilePath + "final"

    PlistWriter(modifiedPlistPath).write(targetProject.plistObj)
    combiner = PlistCombiner(combinedPlistPath, targetProject.plistFilePath, modifiedPlistPath)
    combiner.combine()

    os.remove(targetProject.plistFilePath)
    os.remove(modifiedPlistPath)
    os.rename(combinedPlistPath, targetProject.plistFilePath)
