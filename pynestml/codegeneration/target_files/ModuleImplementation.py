from typing import List

from pynestml.codegeneration.target_files.ModuleLevelFile import ModuleLevelFile
from pynestml.codegeneration.target_files.TargetPaths import TargetPaths
from pynestml.codegeneration.target_files.Templates import Templates
from pynestml.modelprocessor.ASTNeuron import ASTNeuron


class ModuleImplementation(ModuleLevelFile):
    def __init__(self, _neurons):
        # type: (List[ASTNeuron]) -> None
        super(ModuleImplementation, self).__init__(_neurons,
                                                   TargetPaths().module_implementation_path,
                                                   Templates.module_implementation)
