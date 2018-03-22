from pynestml.codegeneration.target_files.TargetPaths import TargetPaths
from pynestml.codegeneration.target_files.Templates import Templates
from pynestml.codegeneration.target_files.ModuleLevelFile import ModuleLevelFile


class CMakeLists(ModuleLevelFile):
    def __init__(self, _neurons):
        super(CMakeLists, self).__init__(_neurons,
                                         TargetPaths().c_make_lists_path,
                                         Templates.c_make_lists)