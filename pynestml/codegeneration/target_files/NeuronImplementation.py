from pynestml.codegeneration.target_files.TargetPaths import TargetPaths
from pynestml.codegeneration.target_files.Templates import Templates
from pynestml.codegeneration.target_files.NeuronFile import NeuronFile


class NeuronImplementation(NeuronFile):

    def __init__(self, _neuron):
        super(NeuronImplementation, self).__init__(_neuron,
                                                   TargetPaths().neuron_implementation_path,
                                                   Templates.neuron_implementation)