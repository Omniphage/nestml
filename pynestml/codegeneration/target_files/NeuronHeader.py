from pynestml.codegeneration.target_files.TargetPaths import TargetPaths
from pynestml.codegeneration.target_files.Templates import Templates
from pynestml.codegeneration.target_files.NeuronFile import NeuronFile


class NeuronHeader(NeuronFile):

    def __init__(self, _neuron):
        super(NeuronHeader, self).__init__(_neuron,
                                           TargetPaths().neuron_header_path,
                                           Templates.neuron_header)