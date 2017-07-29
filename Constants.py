OBJECTS_KEY = "objects"
ROOT_OBJECTS_KEY = "rootObject"
ISA_KEY = "isa"
PRODUCT_REFERENCE_KEY  = "productReference"
MAIN_GROUP_KEY = "mainGroup"
NAME_KEY = "name"
CHILDREN_KEY = "children"
REMOTE_ID_KEY = "remoteGlobalIDString"
PROXY_TYPE_KEY = "proxyType"
REMOTE_REF_KEY = "remoteRef"
PATH_KEY = "path"
FILE_TYPE_KEY = "fileType"
SOURCE_TREE_KEY = "sourceTree"
CONTAINER_PORTAL_KEY = "containerPortal"
REMOTE_INFO_KEY = "remoteInfo"
PROJECT_REFERENCES_KEY = "projectReferences"
PROJECT_REFERENCE_KEY = "ProjectRef"
PRODUCT_GROUP_KEY = "ProductGroup"
BUILD_PHASES_KEY = "buildPhases"
FILES_KEY = "files"
EXPLICIT_FILETYPE_KEY = "explicitFileType"
FILE_REFERENCE_KEY = "fileRef"
TARGET_PROXY_KEY = "targetProxy"
DEPENDENCIES_KEY = "dependencies"
LAST_KNOWN_FILE_TYPE_KEY = "lastKnownFileType"

NATIVE_TARGET_ISA = "PBXNativeTarget"
FILE_REFERENCE_ISA = "PBXFileReference"
CONTAINER_ITEM_PROXY_ISA = "PBXContainerItemProxy"
REFERENCE_PROXY_ISA = "PBXReferenceProxy"
GROUP_ISA = "PBXGroup"
FRAMEWORK_BUILDPHASE_ISA = "PBXFrameworksBuildPhase"
BUILD_FILE_ISA = "PBXBuildFile"
TARGET_DEPENDENCY_ISA = "PBXTargetDependency"

class MissingTargetException(Exception):
    pass

class MissingProjectFileException(Exception):
    pass

class TokenizerException(Exception):
    pass

class ParsingException(Exception):
    pass

class MissingBuildFrameworkException(Exception):
    pass