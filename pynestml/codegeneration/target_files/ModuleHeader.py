from pynestml.codegeneration.target_files.TargetPaths import TargetPaths
from pynestml.codegeneration.target_files.Templates import Templates
from pynestml.codegeneration.target_files.ModuleLevelFile import ModuleLevelFile


class ModuleHeader(ModuleLevelFile):
    def __init__(self, _neurons):
        super(ModuleHeader, self).__init__(_neurons,
                                           TargetPaths().module_header_path,
                                           Templates.module_header)