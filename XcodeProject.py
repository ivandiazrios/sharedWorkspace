import glob
import os
from PlistParser import Parser
from Utils import lazy_property, stripEnd
from Constants import *

class XcodeProject:
    def __init__(self, projectPath):
        self.projectPath = projectPath

    @lazy_property
    def projectName(self):
        return stripEnd(os.path.basename(self.projectFilePath), ".xcodeproj")

    def findSubDirectoryForProjectFile(self):
        directoryToMatchAgaint = os.path.basename(os.path.normpath(self.projectPath))

        files = os.listdir(self.projectPath)
        for file in files:
            fullFilePath = os.path.join(self.projectPath, file)
            if os.path.isdir(fullFilePath) and file.lower() == directoryToMatchAgaint.lower():
                return file

        return None


    @lazy_property
    def projectFilePath(self):
        if not os.path.isdir(self.projectPath):
            raise NotADirectoryException("%s is not a directory" % self.projectPath)

        globPath = os.path.join(self.projectPath, "*.xcodeproj")
        files = glob.glob(globPath)
        if files:
            return files.pop(0)

        # If haven't found it look in a folder with the same name as projectPath directory name -- case insensitive
        subDirectory = self.findSubDirectoryForProjectFile()

        if subDirectory:
            globPath = os.path.join(self.projectPath, "%s/*.xcodeproj" % subDirectory)
            files = glob.glob(globPath)
            if files:
                return files.pop(0)

        raise MissingProjectFileException("Could not find project file in path %s" % self.projectPath)

    @lazy_property
    def plistFilePath(self):
        projectPlistFilePath = os.path.join(self.projectFilePath, "project.pbxproj")
        if not os.path.isfile(projectPlistFilePath):
            raise MissingProjectFileException("Could not project.pbxproj file in path %s" % self.projectFilePath)

        return projectPlistFilePath

    @lazy_property
    def plistObj(self):
        return Parser(self.plistFilePath).parse()

    @lazy_property
    def targets(self):
        return [Target.targetFromKeyValues(id, values) for id, values in self.plistObj[OBJECTS_KEY].iteritems() if values.get(ISA_KEY, None) == NATIVE_TARGET_ISA]

    @lazy_property
    def rootObject(self):
        return self.plistObj[ROOT_OBJECTS_KEY]

    @lazy_property
    def mainGroup(self):
        return self.plistObj[OBJECTS_KEY][self.rootObject][MAIN_GROUP_KEY]

class Target:
    def __init__(self, id, name, productReference, buildPhases):
        self.id = id
        self.name = name
        self.productReference = productReference
        self.buildPhases = buildPhases

    @classmethod
    def targetFromKeyValues(cls, id, values):
        id = id
        name = values[NAME_KEY]
        productReference = values[PRODUCT_REFERENCE_KEY]
        buildPhases = values[BUILD_PHASES_KEY]
        return Target(id, name, productReference, buildPhases)
