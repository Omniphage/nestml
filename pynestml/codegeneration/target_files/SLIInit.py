import os

from pynestml.codegeneration.target_files.TargetPaths import TargetPaths
from pynestml.codegeneration.target_files.Templates import Templates
from pynestml.codegeneration.target_files.ModuleLevelFile import ModuleLevelFile


class SLIInit(ModuleLevelFile):
    def __init__(self, _neurons):
        super(SLIInit, self).__init__(_neurons,
                                      TargetPaths().sli_init_path,
                                      Templates.sli_init)

    @staticmethod
    def create_sli_directory():
        sli_directory_path = os.path.realpath(TargetPaths().sli_directory)
        if not os.path.isdir(sli_directory_path):
            os.makedirs(sli_directory_path)

    def generate(self):
        self.create_sli_directory()
        super(SLIInit, self).generate()