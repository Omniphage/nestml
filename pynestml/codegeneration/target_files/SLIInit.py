import os

from typing import List

from pynestml.codegeneration.target_files.ModuleLevelFile import ModuleLevelFile
from pynestml.codegeneration.target_files.TargetPaths import TargetPaths
from pynestml.codegeneration.target_files.Templates import Templates
from pynestml.modelprocessor.ASTNeuron import ASTNeuron


class SLIInit(ModuleLevelFile):
    def __init__(self, _neurons):
        # type: (List[ASTNeuron]) -> None
        super(SLIInit, self).__init__(_neurons,
                                      TargetPaths().sli_init_path,
                                      Templates.sli_init)

    @staticmethod
    def create_sli_directory():
        # type: () -> None
        sli_directory_path = os.path.realpath(TargetPaths().sli_directory)
        if not os.path.isdir(sli_directory_path):
            os.makedirs(sli_directory_path)

    def generate(self):
        # type: () -> None
        self.create_sli_directory()
        super(SLIInit, self).generate()
