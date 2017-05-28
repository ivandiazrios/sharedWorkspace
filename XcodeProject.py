import glob, os
from PlistParser import Parser
from Utils import lazy_property

class XcodeProject:
    def __init__(self, projectPath):
        self.projectPath = projectPath

    @lazy_property
    def projectName(self):
        return os.path.basename(self.projectFilePath).rstrip(".xcodeproj")

    @lazy_property
    def projectFilePath(self):
        os.chdir(self.projectPath)
        files = glob.glob("*.xcodeproj")
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
        targets = []

        for k, v in self.plistObj["objects"].iteritems():
            if v["isa"] == "PBXNativeTarget":
                targetName = v["productName"]
                targetProductReference = v["productReference"]
                target = Target(targetName, targetProductReference)
                targets.append(target)

        return targets

    @lazy_property
    def rootObject(self):
        return self.plistObj["rootObject"]

    @lazy_property
    def mainGroup(self):
        return self.plistObj["objects"][self.rootObject]["mainGroup"]

class Target:
    def __init__(self, name, productReference):
        self.name = name
        self.productReference = productReference
