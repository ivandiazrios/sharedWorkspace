from Utils import uuid
from collections import defaultdict

class SharedWorkspace(object):
    def __init__(self, targetProject, *sharedProjects):
        self.targetProject = targetProject
        self.sharedProjects = sharedProjects

        self.additionDict = {}
        self.subtractionDict = {}

    def share(self):
        for sharedProject in self.sharedProjects:
            targetToShare = self.targetToShareFromProject(sharedProject)

            self.sharedProject = sharedProject
            self.resetShared()

            self.addFileReference()
            self.addChildToMainGroup()
            self.addContainerItemProxies()
            self.addReferenceProxies()
            self.addProjectReference()
            self.addProductGroup()
            self.replaceDependFrameworkWithSharedWorkspaceLib()
            self.addToTargetDepend()

        return self.additionDict, self.subtractionDict

    def targetToShareFromProject(self, project):


    def resetShared(self):
        self.containerPortal = uuid(24)
        self.libFileId = uuid(24)
        self.productGroupId = uuid(24)
        self.referenceProxyTargetIds = defaultdict(lambda: uuid(24))
        self.containerItemProxyTargetIds = defaultdict(lambda: uuid(24))

    def getKeyOfFirstValueMatchingKeyValue(self, l, *keyValues):
        for k, v in l:
            keyMatches = True

            for (key, value) in keyValues:
                if v.get(key, None) != value:
                    keyMatches = False
                    break

            if keyMatches:
                return k

        return None

    def addChildToMainGroup(self):
        if self.containerPortal in self.targetProject.plistObj["objects"][self.targetProject.mainGroup].get("children", []):
            return

        self.additionDict.setdefault("objects", {}).setdefault(self.targetProject.mainGroup, {}).setdefault("children", []).insert(0, self.containerPortal)

    def addContainerItemProxies(self):
        containerItemProxies = self.getAllObjectsWithIsa("PBXContainerItemProxy")

        for target in self.sharedProject.targets:
            containerItemProxyTargetId = self.getKeyOfFirstValueMatchingKeyValue(containerItemProxies, ("remoteGlobalIDString", target.productReference), ("proxyType", 2))
            if containerItemProxyTargetId:
                self.containerItemProxyTargetIds[target.productReference] = containerItemProxyTargetId
                continue

            self.additionDict.setdefault("objects", {})[self.containerItemProxyTargetIds[target.productReference]] = {
                "isa": "PBXContainerItemProxy",
                "containerPortal": self.containerPortal,
                "proxyType": 2,
                "remoteGlobalIDString": target.productReference,
                "remoteInfo": target.remoteInfo
            }

    def getAllObjectsWithIsa(self, isa):
        return filter(lambda (k,v): v.get("isa", None) == isa, self.targetProject.plistObj["objects"].iteritems())

    def containerPortalForProject(self, project):
        fileReferences = self.getAllObjectsWithIsa("PBXFileReference")
        projectName = project.projectName + ".xcodeproj"
        return self.getKeyOfFirstValueMatchingKeyValue(fileReferences, ("name", projectName))

    def addFileReference(self):
        containerPortal = self.containerPortalForProject(self.sharedProject)
        if containerPortal:
            self.containerPortal = containerPortal
            return

        self.additionDict.setdefault("objects", {})[self.containerPortal] = {
            "isa": "PBXFileReference",
            "lastKnownFileType": "\"wrapper.pb-project\"",
            "name": self.sharedProject.projectName + ".xcodeproj",
            "path": "\"" + self.sharedProject.projectFilePath + "\"",
            "sourceTree": "\"<group>\""
        }

    def addProductGroup(self):
        currentChildren = self.targetProject.plistObj["objects"].get(self.productGroupId, {}).get("children", [])
        childrenToAdd = [self.referenceProxyTargetIds[target.productReference] for target in self.sharedProject.targets]
        childrenToAdd = list(set(childrenToAdd) - set(currentChildren))

        if not childrenToAdd:
            return

        if self.targetProject.plistObj["objects"].get(self.productGroupId, None):
            self.additionDict.setdefault("objects", {})[self.productGroupId] = {
                "children": childrenToAdd,
            }
        else:
            self.additionDict.setdefault("objects", {})[self.productGroupId] = {
                "isa": "PBXGroup",
                "children": childrenToAdd,
                "name": "Products",
                "sourceTree": "\"<group>\""
            }


    def addReferenceProxies(self):
        referenceProxyIds = self.getAllObjectsWithIsa("PBXReferenceProxy")

        for target in self.sharedProject.targets:
            referenceProxyId = self.getKeyOfFirstValueMatchingKeyValue(referenceProxyIds, ("remoteRef", self.containerItemProxyTargetIds[target.productReference]))
            if referenceProxyId:
                self.referenceProxyTargetIds[target.productReference] = referenceProxyId
                continue

            self.additionDict.setdefault("objects", {})[self.referenceProxyTargetIds[target.productReference]] = {
                "isa": "PBXReferenceProxy",
                "fileType": self.fileTypeForContainerProxy(self.containerItemProxyTargetIds[target.productReference]),
                "path": "%s" % self.sharedProject.plistObj["objects"][target.productReference]["path"],
                "remoteRef": self.containerItemProxyTargetIds[target.productReference],
                "sourceTree": "BUILT_PRODUCTS_DIR"
            }

    def fileTypeForContainerProxy(self, containerProxyId):
        remoteId = self.additionDict["objects"][containerProxyId]["remoteGlobalIDString"]
        return self.sharedProject.plistObj["objects"][remoteId]["explicitFileType"]

    def idOfTargetToAddToFrameworkPhase(self):
        for target in self.sharedProject.targets:
            if self.sharedProject.plistObj["objects"][target.productReference]["path"].startswith("lib"):
                return self.referenceProxyTargetIds[target.productReference]

    def addLibBuildFile(self):
        buildFiles = self.getAllObjectsWithIsa("PBXBuildFile")
        libFileId = self.getKeyOfFirstValueMatchingKeyValue(buildFiles, ("fileRef", self.idOfTargetToAddToFrameworkPhase()))
        if libFileId:
            self.libFileId = libFileId
            return

        self.additionDict.setdefault("objects", {})[self.libFileId] = {
            "isa": "PBXBuildFile",
            "fileRef": self.idOfTargetToAddToFrameworkPhase()
        }

    def addProjectReference(self):
        projectId = self.targetProject.plistObj["rootObject"]
        projectReferences = self.targetProject.plistObj["objects"].get(projectId, {}).get("projectReferences", [])
        for projectReference in projectReferences:
            if projectReference.get("ProjectRef", None) == self.containerPortal:
                self.productGroupId = projectReference["ProductGroup"]
                return

        projectReference = {
            "ProductGroup": self.productGroupId,
            "ProjectRef": self.containerPortal
        }

        self.additionDict.setdefault("objects", {}).setdefault(projectId, {}).setdefault("projectReferences", []).insert(0, projectReference)

    def replaceDependFrameworkWithSharedWorkspaceLib(self):
        allFrameworkBuildPhases, _ = zip(*self.getAllObjectsWithIsa("PBXFrameworksBuildPhase"))
        allTargets = self.getAllObjectsWithIsa("PBXNativeTarget")

        targetName = self.targetProject.projectName
        targets = [target for id, target in allTargets if target["name"] == targetName]

        targetFrameworkPhase = None

        for target in targets:
            targetFrameworkPhase = set(allFrameworkBuildPhases) & set(target["buildPhases"])
            if len(targetFrameworkPhase):
                targetFrameworkPhase = list(targetFrameworkPhase)[0]
            break

        frameworkPhaseFiles = self.targetProject.plistObj["objects"][targetFrameworkPhase]["files"]

        for file in frameworkPhaseFiles:
            fileref = self.targetProject.plistObj["objects"][file]["fileRef"]
            if self.targetProject.plistObj["objects"][fileref].get("name", "").startswith(self.sharedProject.projectName):
                fileToRemove = file
                self.subtractionDict.setdefault("objects", {}).setdefault(targetFrameworkPhase, {}).setdefault("files", []).insert(0, fileToRemove)
                self.subtractionDict["objects"][fileToRemove] = None
                break

        self.addLibBuildFile()
        if self.libFileId not in self.targetProject.plistObj["objects"].get(targetFrameworkPhase, {}).get("files", []):
            self.additionDict.setdefault("objects", {}).setdefault(targetFrameworkPhase, {}).setdefault("files", []).insert(0, self.libFileId)

    def addToTargetDepend(self):
        shareTarget = None
        for target in self.sharedProject.targets:
            if self.sharedProject.plistObj["objects"][target.productReference]["path"].startswith("lib"):
                shareTarget = target

        if not shareTarget:
            return

        containerItemProxies = self.getAllObjectsWithIsa("PBXContainerItemProxy")
        dependProxy = self.getKeyOfFirstValueMatchingKeyValue(containerItemProxies, ("containerPortal", self.containerPortal), ("remoteGlobalIDString", target.id), ("proxyType", 1))
        if not dependProxy:
            dependProxy = uuid()
            self.additionDict.setdefault("objects", {})[dependProxy] = {
                "isa": "PBXContainerItemProxy",
                "containerPortal": self.containerPortal,
                "proxyType": 1,
                "remoteGlobalIDString": shareTarget.id,
                "remoteInfo": shareTarget.remoteInfo
            }

        targetDependencies = self.getAllObjectsWithIsa("PBXTargetDependency")
        targetDependency = self.getKeyOfFirstValueMatchingKeyValue(targetDependencies, ("targetProxy", dependProxy))
        if not targetDependency:
            targetDependency = uuid(24)
            self.additionDict.setdefault("objects", {})[targetDependency] = {
                "isa": "PBXTargetDependency",
                "name": shareTarget.remoteInfo,
                "targetProxy": dependProxy
            }

        targetName = self.targetProject.projectName
        targets = [target for target in self.targetProject.targets if target.remoteInfo == targetName]
        if not targets:
            return

        target = targets[0]
        if targetDependency not in self.targetProject.plistObj.get("objects", {}).get(target.id, {}).get("dependencies", []):
            self.additionDict.setdefault("objects", {}).setdefault(target.id, {}).setdefault("dependencies", []).insert(0, targetDependency)
