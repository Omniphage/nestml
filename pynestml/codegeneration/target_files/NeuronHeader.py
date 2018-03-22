from pynestml.codegeneration.target_files.NeuronFile import NeuronFile
from pynestml.codegeneration.target_files.TargetPaths import TargetPaths
from pynestml.codegeneration.target_files.Templates import Templates
from pynestml.modelprocessor.ASTNeuron import ASTNeuron


class NeuronHeader(NeuronFile):

    def __init__(self, _neuron):
        # type: (ASTNeuron) -> None
        super(NeuronHeader, self).__init__(_neuron,
                                           TargetPaths().neuron_header_path,
                                           Templates.neuron_header)
