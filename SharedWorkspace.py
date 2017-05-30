from Utils import uuid, lazy_property
from collections import defaultdict

class SharedWorkspace(object):
    def __init__(self, targetProject, sharedProject):
        self.targetProject = targetProject
        self.sharedProject = sharedProject

        self.outputPlist = self.targetProject.plistObj

    def share(self):
        self.addProxySection()
        self.addFileReference()
        self.addChildToMainGroup()
        self.addProductGroup()

    def addChildToMainGroup(self):
        self.outputPlist["objects"][self.targetProject.mainGroup]["children"].insert(0, self.containerPortals[self.sharedProject.projectName])

    def addProxySection(self):
        self.outputPlist["objects"][uuid()] = {
            "isa": "PBXContainerItemProxy",
            "containerPortal": self.containerPortals[self.sharedProject.projectName],
            "proxyType": 2,
            "remoteGlobalIDString": self.sharedProject.targets[0].productReference,
            "remoteInfo": self.sharedProject.projectName
        }

    def addFileReference(self):
        self.outputPlist["objects"][self.containerPortals[self.sharedProject.projectName]] = {

            "isa": "PBXFileReference",
            "lastKnownFileType": "\"wrapper.pb-project\"",
            "name": self.sharedProject.projectName + ".xcodeproj",
            "path": self.sharedProject.projectFilePath,
            "sourceTree": "\"<group>\""
        }

    def addProductGroup(self):
        self.outputPlist["objects"][self.productGroupId] = {
            "isa": "PBXGroup",
            "children": [self.referenceProxyId],
            "name": "Products",
            "sourceTree": "\"<group>\""
        }

    @lazy_property
    def containerPortals(self):
        return defaultdict(lambda: uuid(24))

    @lazy_property
    def productGroupId(self):
        return uuid(24)

    @lazy_property
    def referenceProxyId(self):
        return uuid(24)
