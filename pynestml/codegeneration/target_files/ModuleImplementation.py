from pynestml.codegeneration.target_files.TargetPaths import TargetPaths
from pynestml.codegeneration.target_files.Templates import Templates
from pynestml.codegeneration.target_files.ModuleLevelFile import ModuleLevelFile


class ModuleImplementation(ModuleLevelFile):
    def __init__(self, _neurons):
        super(ModuleImplementation, self).__init__(_neurons,
                                                   TargetPaths().module_implementation_path,
                                                   Templates.module_implementation)