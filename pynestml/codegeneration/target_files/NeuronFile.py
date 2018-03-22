from jinja2 import Template
from typing import List

from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.codegeneration.GSLReferenceConverter import GSLReferenceConverter
from pynestml.codegeneration.LegacyExpressionPrinter import LegacyExpressionPrinter
from pynestml.codegeneration.NestAssignmentsHelper import NestAssignmentsHelper
from pynestml.codegeneration.NestDeclarationsHelper import NestDeclarationsHelper
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.codegeneration.NestPrinter import NestPrinter
from pynestml.codegeneration.NestReferenceConverter import NESTReferenceConverter
from pynestml.codegeneration.target_files.TargetFile import TargetFile
from pynestml.frontend.FrontendConfiguration import FrontendConfiguration
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.OdeTransformer import OdeTransformer


class NeuronFile(TargetFile):
    def __init__(self, _neuron, _path, _template):
        # type: (ASTNeuron, str, Template) -> None
        super(NeuronFile, self).__init__(_path % _neuron.getName(),
                                         _template)
        self.neuron = _neuron

    def setup_namespace(self):
        # type: () -> dict
        converter = NESTReferenceConverter()
        legacy_pretty_printer = LegacyExpressionPrinter(_reference_converter=converter)
        printer = NestPrinter(_expressionPrettyPrinter=legacy_pretty_printer)
        gsl_converter = GSLReferenceConverter()
        gsl_printer = LegacyExpressionPrinter(_reference_converter=gsl_converter)
        namespace = {'neuronName': self.neuron.getName(),
                     'neuron': self.neuron,
                     'moduleName': FrontendConfiguration.getModuleName(),
                     'printer': printer,
                     'assignments': NestAssignmentsHelper(),
                     'names': NestNamesConverter(),
                     'declarations': NestDeclarationsHelper(),
                     'utils': ASTUtils(),
                     'idemPrinter': LegacyExpressionPrinter(),
                     'outputEvent': printer.printOutputEvent(self.neuron.getBody()),
                     'isSpikeInput': ASTUtils.isSpikeInput(self.neuron.getBody()),
                     'isCurrentInput': ASTUtils.isCurrentInput(self.neuron.getBody()),
                     'odeTransformer': OdeTransformer(),
                     'printerGSL': gsl_printer}
        self.define_solver_type(namespace, self.neuron)
        return namespace

    def define_solver_type(self, _namespace, _neuron):
        # type: (dict, ASTNeuron) -> None
        """For a handed over neuron this method enriches the namespace by methods which are used to solve
        odes."""
        _namespace['useGSL'] = False
        if _neuron.getEquationsBlocks() is not None and len(_neuron.getEquationsBlocks().getDeclarations()) > 0:
            if (not self.function_shape_exists(_neuron.getEquationsBlocks().getOdeShapes())) or \
                    len(_neuron.getEquationsBlocks().getOdeEquations()) > 1:
                _namespace['names'] = GSLNamesConverter()
                _namespace['useGSL'] = True
                converter = NESTReferenceConverter(_usesGSL=True)
                legacy_pretty_printer = LegacyExpressionPrinter(_reference_converter=converter)
                _namespace['printer'] = NestPrinter(_expressionPrettyPrinter=legacy_pretty_printer)
        return

    @classmethod
    def function_shape_exists(cls, _shapes):
        # type: (List[ASTOdeShape]) -> bool
        """For a handed over list of shapes this method checks if a single shape exits with differential order of 0."""
        for shape in _shapes:
            if isinstance(shape, ASTOdeShape) and shape.getVariable().getDifferentialOrder() == 0:
                return True
        return False
