from jinja2 import Template
from typing import List

from pynestml.codegeneration.target_files.TargetFile import TargetFile
from pynestml.frontend.FrontendConfiguration import FrontendConfiguration
from pynestml.modelprocessor.ASTNeuron import ASTNeuron


class ModuleLevelFile(TargetFile):
    def __init__(self, _neurons, _path, _template):
        # type: (List[ASTNeuron], str, Template) -> None
        super(ModuleLevelFile, self).__init__(_path, _template)
        self.neurons = _neurons

    def setup_namespace(self):
        # type: () -> dict
        return {'neurons': self.neurons, 'moduleName': FrontendConfiguration.getModuleName()}
