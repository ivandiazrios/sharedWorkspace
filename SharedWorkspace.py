from Utils import uuid, lazy_property
from collections import defaultdict

class SharedWorkspace(object):
    def __init__(self, targetProject, sharedProject):
        self.targetProject = targetProject
        self.sharedProject = sharedProject

        self.outputPlist = self.targetProject.plistObj

    def share(self):
        self.addFileReference()
        self.addChildToMainGroup()
        self.addContainerItemProxies()
        self.addReferenceProxies()
        self.addProductGroup()
        self.addProjectReference()
        self.replaceDependFrameworkWithSharedWorkspaceLib()

    def addChildToMainGroup(self):
        self.outputPlist["objects"][self.targetProject.mainGroup]["children"].insert(0, self.containerPortal)

    def addContainerItemProxies(self):
        for target in self.sharedProject.targets:
            self.outputPlist["objects"][self.containerItemProxyTargetIds[target.productReference]] = {
                "isa": "PBXContainerItemProxy",
                "containerPortal": self.containerPortal,
                "proxyType": 2,
                "remoteGlobalIDString": target.productReference,
                "remoteInfo": self.sharedProject.projectName
            }

    def addFileReference(self):
        self.outputPlist["objects"][self.containerPortal] = {
            "isa": "PBXFileReference",
            "lastKnownFileType": "\"wrapper.pb-project\"",
            "name": self.sharedProject.projectName + ".xcodeproj",
            "path": "\"" + self.sharedProject.projectFilePath + "\"",
            "sourceTree": "\"<group>\""
        }

    def addProductGroup(self):
        self.outputPlist["objects"][self.productGroupId] = {
            "isa": "PBXGroup",
            "children": [self.referenceProxyTargetIds[target.productReference] for target in self.sharedProject.targets],
            "name": "Products",
            "sourceTree": "\"<group>\""
        }

    def addReferenceProxies(self):
        for target in self.sharedProject.targets:
            self.outputPlist["objects"][self.referenceProxyTargetIds[target.productReference]] = {
                "isa": "PBXReferenceProxy",
                "fileType": "wrapper.framework",
                "path": "%s" % self.sharedProject.plistObj["objects"][target.productReference]["path"],
                "remoteRef": self.containerItemProxyTargetIds[target.productReference],
                "sourceTree": "BUILT_PRODUCTS_DIR"
            }

    def addProjectReference(self):
        projectId = self.targetProject.plistObj["rootObject"]
        projectReferences = self.targetProject.plistObj["objects"][projectId].get("projectReferences", [])

        projectReference = {
            "ProductGroup": self.productGroupId,
            "ProjectRef": self.containerPortal
        }

        projectReferences.append(projectReference)
        self.targetProject.plistObj["objects"][projectId]["projectReferences"] = projectReferences

    def replaceDependFrameworkWithSharedWorkspaceLib(self):
        allFrameworkBuildPhases = [k for k, v in self.getAllObjectsOfISA(self.targetProject.plistObj, "PBXFrameworksBuildPhase")]
        allTargets = self.getAllObjectsOfISA(self.targetProject.plistObj, "PBXNativeTarget")

        targetName = self.targetProject.projectName
        targets = [target for id, target in allTargets if target["name"] == targetName]

        for target in targets:
            targetFrameworkPhase = set(allFrameworkBuildPhases) & set(target["buildPhases"])
            if len(targetFrameworkPhase):
                targetFrameworkPhase = list(targetFrameworkPhase)[0]

            frameworkPhaseFiles = self.targetProject.plistObj["objects"][targetFrameworkPhase]["files"]

            for file in frameworkPhaseFiles:
                fileref = self.targetProject.plistObj["objects"][file]["fileRef"]
                if self.targetProject.plistObj["objects"][fileref]["name"].startswith(self.sharedProject.projectName):
                    fileToRemove = file
                    break

            frameworkPhaseFiles.remove(fileToRemove)

    @lazy_property
    def referenceProxyTargetIds(self):
        return defaultdict(lambda: uuid(24))

    @lazy_property
    def containerItemProxyTargetIds(self):
        return defaultdict(lambda: uuid(24))

    @lazy_property
    def containerPortal(self):
        return uuid(24)

    @lazy_property
    def productGroupId(self):
        return uuid(24)

    def getAllObjectsOfISA(self, plist, isa):
        return [(k, v) for k, v in plist["objects"].iteritems() if v["isa"] == isa]

