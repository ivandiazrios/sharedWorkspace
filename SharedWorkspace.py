from Utils import uuid, deepDictMerge
from Constants import *

class SharedWorkspace(object):
    def __init__(self, targetProject, *sharedProjects):
        self.targetProject = targetProject
        self.sharedProjects = sharedProjects

    def share(self, targetTargetName=None):

        self.finalAdditionDict, self.finalSubtractionDict = {}, {}

        try:
            targetTarget = self.targetTargetFor(targetTargetName)
        except Exception as e:
            print "Error: %s" % e.message
            return None, None

        for sharedProject in self.sharedProjects:

            self.isaObjectCache = {}
            self.additionDict, self.subtractionDict = {}, {}

            try:
                self.shareProject(targetTarget, sharedProject)
            except Exception as e:
                print "Could not share %s: %s" % sharedProject.projectName, e.message
            else:
                deepDictMerge(self.additionDict, self.finalAdditionDict)
                deepDictMerge(self.subtractionDict, self.finalSubtractionDict)

        return self.finalAdditionDict, self.finalSubtractionDict

    def shareProject(self, target, sharedProject):
        sharedTarget= self.targetToShareFromProject(sharedProject)

        containerPortal = self.addContainerPortal(sharedProject)

        self.addChildToMainGroup(containerPortal)

        containerItemProxyIdForTargetReferenceDict = self.addContainerItemProxies(sharedProject, containerPortal)
        referenceProxyTargetIdForProductReference = self.addReferenceProxies(sharedProject,
                                                                             containerItemProxyIdForTargetReferenceDict)
        productGroupId = self.addProjectReference(containerPortal)

        self.addProductGroup(sharedProject, productGroupId, referenceProxyTargetIdForProductReference)
        self.replaceDependFrameworkWithSharedWorkspaceLib(target, sharedTarget,
                                                          referenceProxyTargetIdForProductReference)
        self.addToTargetDepend(target, sharedTarget, containerPortal)

    def targetToShareFromProject(self, project):
        targetToShare = next((target for target in project.targets if
                              project.plistObj["objects"][target.productReference]["path"].startswith("lib")), None)
        if not targetToShare:
            raise MissingTargetException("Missing target to share")

        return targetToShare

    def targetTargetFor(self, targetName):
        if not targetName:
            # Use default target name of project if none specified
            targetName = self.targetProject.projectName

        target = next((target for target in self.targetProject.targets if target.name == targetName), None)
        if not target:
            raise MissingTargetException("Missing target %s" % targetName)

        return target

    def getKeyOfFirstValueMatchingKeyValue(self, l, *keyValues):
        dictContainsKeyValues = lambda dict: all((dict.get(k, None) == v for k, v in keyValues))
        return next((k for k,v in l if dictContainsKeyValues(v)), None)

    def addChildToMainGroup(self, containerPortal):
        if containerPortal in self.targetProject.plistObj[OBJECTS_KEY][self.targetProject.mainGroup].get(CHILDREN_KEY, []):
            return

        self.additionDict.setdefault(OBJECTS_KEY, {}).setdefault(self.targetProject.mainGroup, {}).setdefault(CHILDREN_KEY, []).insert(0, containerPortal)

    def addContainerItemProxies(self, sharedProject, containerPortal):
        containerItemProxies = self.getAllObjectsWithIsa(CONTAINER_ITEM_PROXY_ISA)
        containerItemProxyIdForTargetReferenceDict = {}

        for target in sharedProject.targets:
            containerItemProxyTargetId = self.getKeyOfFirstValueMatchingKeyValue(containerItemProxies, (REMOTE_ID_KEY, target.productReference), (PROXY_TYPE_KEY, 2))
            if containerItemProxyTargetId:
                containerItemProxyIdForTargetReferenceDict[target.productReference] = containerItemProxyTargetId
                continue

            containerItemProxyTargetId = uuid(24)
            containerItemProxyIdForTargetReferenceDict[target.productReference] = containerItemProxyTargetId

            self.additionDict.setdefault(OBJECTS_KEY, {})[containerItemProxyTargetId] = {
                ISA_KEY: CONTAINER_ITEM_PROXY_ISA,
                CONTAINER_PORTAL_KEY: containerPortal,
                PROXY_TYPE_KEY: 2,
                REMOTE_ID_KEY: target.productReference,
                REMOTE_INFO_KEY: target.name
            }

        return containerItemProxyIdForTargetReferenceDict

    def getAllObjectsWithIsa(self, isa):
        objectsForIsa = self.isaObjectCache.get(isa, None)
        if objectsForIsa:
            return objectsForIsa
        else:
            objectsForIsa = filter(lambda (k,v): v.get(ISA_KEY, None) == isa, self.targetProject.plistObj[OBJECTS_KEY].iteritems())
            self.isaObjectCache[isa] = objectsForIsa
            return objectsForIsa

    def containerPortalForProject(self, project):
        fileReferences = self.getAllObjectsWithIsa(FILE_REFERENCE_ISA)
        projectName = project.projectName + ".xcodeproj"
        return self.getKeyOfFirstValueMatchingKeyValue(fileReferences, (NAME_KEY, projectName))

    def addContainerPortal(self, sharedProject):
        containerPortal = self.containerPortalForProject(sharedProject)
        if containerPortal:
            return containerPortal

        containerPortal = uuid(24)

        self.additionDict.setdefault(OBJECTS_KEY, {})[containerPortal] = {
            ISA_KEY: FILE_REFERENCE_ISA,
            LAST_KNOWN_FILE_TYPE_KEY: "\"wrapper.pb-project\"",
            NAME_KEY: sharedProject.projectName + ".xcodeproj",
            PATH_KEY: '"%s"' % sharedProject.projectFilePath,
            SOURCE_TREE_KEY: "\"<group>\""
        }

        return containerPortal

    def addProductGroup(self, sharedProject, productGroupId, referenceProxyTargetIds):
        currentChildren = self.targetProject.plistObj[OBJECTS_KEY].get(productGroupId, {}).get(CHILDREN_KEY, [])
        childrenToAdd = [referenceProxyTargetIds[target.productReference] for target in sharedProject.targets]
        childrenToAdd = list(set(childrenToAdd) - set(currentChildren))

        if not childrenToAdd:
            return

        if self.targetProject.plistObj[OBJECTS_KEY].get(productGroupId, None):
            self.additionDict.setdefault(OBJECTS_KEY, {})[productGroupId] = {
                CHILDREN_KEY: childrenToAdd,
            }
        else:
            self.additionDict.setdefault(OBJECTS_KEY, {})[productGroupId] = {
                ISA_KEY: GROUP_ISA,
                CHILDREN_KEY: childrenToAdd,
                NAME_KEY: "Products",
                SOURCE_TREE_KEY: "\"<group>\""
            }


    def addReferenceProxies(self, sharedProject, containerItemProxyTargetIds):
        referenceProxyIds = self.getAllObjectsWithIsa(REFERENCE_PROXY_ISA)
        referenceProxyTargetIdForProductReference = {}

        for target in sharedProject.targets:
            targetContainerItemProxyId = containerItemProxyTargetIds[target.productReference]
            referenceProxyId = self.getKeyOfFirstValueMatchingKeyValue(referenceProxyIds, (REMOTE_REF_KEY, targetContainerItemProxyId ))

            if referenceProxyId:
                referenceProxyTargetIdForProductReference[target.productReference] = referenceProxyId
                continue

            referenceProxyId = uuid(24)
            referenceProxyTargetIdForProductReference[target.productReference] = referenceProxyId

            self.additionDict.setdefault(OBJECTS_KEY, {})[referenceProxyId] = {
                ISA_KEY: REFERENCE_PROXY_ISA,
                FILE_TYPE_KEY: self.fileTypeForContainerProxy(sharedProject, targetContainerItemProxyId),
                PATH_KEY: "%s" % sharedProject.plistObj[OBJECTS_KEY][target.productReference][PATH_KEY],
                REMOTE_REF_KEY: targetContainerItemProxyId,
                SOURCE_TREE_KEY: "BUILT_PRODUCTS_DIR"
            }

        return referenceProxyTargetIdForProductReference

    def fileTypeForContainerProxy(self, sharedProject, containerProxyId):
        remoteId = self.additionDict[OBJECTS_KEY][containerProxyId][REMOTE_ID_KEY]
        return sharedProject.plistObj[OBJECTS_KEY][remoteId][EXPLICIT_FILETYPE_KEY]

    def addProjectReference(self, containerPortal):
        projectId = self.targetProject.plistObj[ROOT_OBJECTS_KEY]
        projectReferences = self.targetProject.plistObj[OBJECTS_KEY].get(projectId, {}).get(PROJECT_REFERENCES_KEY, [])

        projectReference = next((projectReference for projectReference in projectReferences if projectReference.get(PROJECT_REFERENCE_KEY, None) == containerPortal), None)
        if projectReference:
            return projectReference[PRODUCT_GROUP_KEY]

        productGroupId = uuid(24)

        projectReference = {
            PRODUCT_GROUP_KEY: productGroupId,
            PROJECT_REFERENCE_KEY: containerPortal
        }

        self.additionDict.setdefault(OBJECTS_KEY, {}).setdefault(projectId, {}).setdefault(PROJECT_REFERENCES_KEY, []).insert(0, projectReference)

        return productGroupId

    def targetFrameworkPhaseForTarget(self, target):
        frameworkBuildPhases, _ = zip(*self.getAllObjectsWithIsa(FRAMEWORK_BUILDPHASE_ISA))

        overlappingFrameworkPhases = list(set(frameworkBuildPhases) & set(target.buildPhases))
        if not overlappingFrameworkPhases:
            raise MissingBuildFrameworkException("Target %s is missing a framework link phase" % target.name)

        return overlappingFrameworkPhases.pop(0)  # There should only be one

    def frameworkNameForTarget(self, target):
        targetName = target.name
        if targetName.endswith("Lib"):
            targetName = targetName[:-3]

        return targetName + ".framework"

    def replaceDependFrameworkWithSharedWorkspaceLib(self, targetTarget, sharedTarget, referenceProxyTargetIdForProductReference):
        targetFrameworkPhase = self.targetFrameworkPhaseForTarget(targetTarget)
        targetFrameworkPhaseFiles = self.targetProject.plistObj[OBJECTS_KEY][targetFrameworkPhase][FILES_KEY]

        shouldAddLibBuildFile = True
        referenceIdForTargetTarget = referenceProxyTargetIdForProductReference[sharedTarget.productReference]
        frameworkNameToRemove = self.frameworkNameForTarget(sharedTarget)

        # Iterate through files until we find our framework one... then remove it.
        for file in targetFrameworkPhaseFiles:
            fileRefId = self.targetProject.plistObj[OBJECTS_KEY][file][FILE_REFERENCE_KEY]
            fileName = self.targetProject.plistObj[OBJECTS_KEY].get(fileRefId, {}).get(NAME_KEY, "")
            if fileName.lower() == frameworkNameToRemove.lower():
                self.subtractionDict.setdefault(OBJECTS_KEY, {}).setdefault(targetFrameworkPhase, {}).setdefault(FILES_KEY, []).insert(0, file)
                self.subtractionDict[OBJECTS_KEY][file] = None
            elif fileRefId == referenceIdForTargetTarget:
                shouldAddLibBuildFile = False

        if shouldAddLibBuildFile:

            libFileId = uuid(24)

            self.additionDict.setdefault(OBJECTS_KEY, {})[libFileId] = {
                ISA_KEY: BUILD_FILE_ISA,
                FILE_REFERENCE_KEY: referenceIdForTargetTarget
            }

            self.additionDict.setdefault(OBJECTS_KEY, {}).setdefault(targetFrameworkPhase, {}).setdefault(FILES_KEY, []).insert(0, libFileId)

    def addToTargetDepend(self, targetTarget, shareTarget, containerPortal):

        containerItemProxies = self.getAllObjectsWithIsa(CONTAINER_ITEM_PROXY_ISA)
        dependProxy = self.getKeyOfFirstValueMatchingKeyValue(containerItemProxies, (CONTAINER_PORTAL_KEY, containerPortal), (REMOTE_ID_KEY, shareTarget.id), (PROXY_TYPE_KEY, 1))
        if not dependProxy:
            dependProxy = uuid()
            self.additionDict.setdefault(OBJECTS_KEY, {})[dependProxy] = {
                ISA_KEY: CONTAINER_ITEM_PROXY_ISA,
                CONTAINER_PORTAL_KEY: containerPortal,
                PROXY_TYPE_KEY: 1,
                REMOTE_ID_KEY: shareTarget.id,
                REMOTE_INFO_KEY: shareTarget.name
            }

        targetDependencies = self.getAllObjectsWithIsa(TARGET_DEPENDENCY_ISA)
        targetDependency = self.getKeyOfFirstValueMatchingKeyValue(targetDependencies, (TARGET_PROXY_KEY, dependProxy))
        if not targetDependency:
            targetDependency = uuid(24)
            self.additionDict.setdefault(OBJECTS_KEY, {})[targetDependency] = {
                ISA_KEY: TARGET_DEPENDENCY_ISA,
                NAME_KEY: shareTarget.name,
                TARGET_PROXY_KEY: dependProxy
            }

        if targetDependency not in self.targetProject.plistObj.get(OBJECTS_KEY, {}).get(targetTarget.id, {}).get(DEPENDENCIES_KEY, []):
            self.additionDict.setdefault(OBJECTS_KEY, {}).setdefault(targetTarget.id, {}).setdefault(DEPENDENCIES_KEY, []).insert(0, targetDependency)
