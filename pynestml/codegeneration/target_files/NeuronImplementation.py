from pynestml.codegeneration.target_files.NeuronFile import NeuronFile
from pynestml.codegeneration.target_files.TargetPaths import TargetPaths
from pynestml.codegeneration.target_files.Templates import Templates
from pynestml.modelprocessor.ASTNeuron import ASTNeuron


class NeuronImplementation(NeuronFile):

    def __init__(self, _neuron):
        # type: (ASTNeuron) -> None
        super(NeuronImplementation, self).__init__(_neuron,
                                                   TargetPaths().neuron_implementation_path,
                                                   Templates.neuron_implementation)
