from pynestml.codegeneration.target_files.TargetFile import TargetFile
from pynestml.frontend.FrontendConfiguration import FrontendConfiguration


class ModuleLevelFile(TargetFile):
    def __init__(self, _neurons, _path, _template):
        super(ModuleLevelFile, self).__init__(_path, _template)
        self.neurons = _neurons

    def setup_namespace(self):
        return {'neurons': self.neurons, 'moduleName': FrontendConfiguration.getModuleName()}