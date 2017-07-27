import glob
import os
from PlistParser import Parser
from Utils import lazy_property
from Constants import *

class XcodeProject:
    def __init__(self, projectPath):
        self.projectPath = projectPath

    @lazy_property
    def projectName(self):
        return os.path.basename(self.projectFilePath).rstrip(".xcodeproj")

    @lazy_property
    def projectFilePath(self):
        globPath = os.path.join(self.projectPath, "*.xcodeproj")
        files = glob.glob(globPath)
        assert len(files) == 1
        return os.path.join(os.getcwd(), files[0])

    @lazy_property
    def plistFilePath(self):
        projectPlistFilePath = os.path.join(self.projectFilePath, "project.pbxproj")
        assert os.path.isfile(projectPlistFilePath)
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
    def __init__(self, id, name, productReference):
        self.id = id
        self.name = name
        self.productReference = productReference

    @classmethod
    def targetFromKeyValues(cls, id, values):
        id = id
        name = values[PRODUCT_NAME_KEY]
        productReference = values[PRODUCT_REFERENCE_KEY]
        return Target(id, name, productReference)
