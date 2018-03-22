#
# NestGenerator.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.
import os
from copy import deepcopy

from jinja2 import Environment, FileSystemLoader

from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.codegeneration.GSLReferenceConverter import GSLReferenceConverter
from pynestml.codegeneration.LegacyExpressionPrinter import LegacyExpressionPrinter
from pynestml.codegeneration.NestAssignmentsHelper import NestAssignmentsHelper
from pynestml.codegeneration.NestDeclarationsHelper import NestDeclarationsHelper
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.codegeneration.NestPrinter import NestPrinter
from pynestml.codegeneration.NestReferenceConverter import NESTReferenceConverter
from pynestml.frontend.FrontendConfiguration import FrontendConfiguration
from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
from pynestml.modelprocessor.ASTSymbolTableVisitor import ASTSymbolTableVisitor
from pynestml.solver.EquationsBlockProcessor import EquationsBlockProcessor
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages
from pynestml.utils.OdeTransformer import OdeTransformer


class TemplateEnvironment(object):
    template_c_make_lists = None
    template_module_class = None
    template_module_header = None
    template_sli_init = None
    template_neuron_header = None
    template_neuron_implementation = None

    def __init__(self):
        # setup the environment
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templatesNEST')))
        self.template_c_make_lists = env.get_template('CMakeLists.jinja2')
        self.template_module_class = env.get_template('ModuleClass.jinja2')
        self.template_module_header = env.get_template('ModuleHeader.jinja2')
        self.template_sli_init = env.get_template('SLI_Init.jinja2')
        self.template_neuron_header = env.get_template('NeuronHeader.jinja2')
        self.template_neuron_implementation = env.get_template('NeuronClass.jinja2')
        return


class TemplateRenderer(object):
    def __init__(self, _environment=TemplateEnvironment()):
        self.environment = _environment

    def render_module_header(self, _namespace):
        return self.environment.template_module_header.render(_namespace)

    def render_module_class(self, _namespace):
        return self.environment.template_module_class.render(_namespace)

    def render_c_make_lists(self, _namespace):
        return self.environment.template_c_make_lists.render(_namespace)

    def render_sli_init(self, _namespace):
        return self.environment.template_sli_init.render(_namespace)

    def render_neuron_header(self, _namespace):
        return self.environment.template_neuron_header.render(_namespace)

    def render_neuron_implementation(self, _namespace):
        return self.environment.template_neuron_implementation.render(_namespace)


class NestCodeGenerator(object):
    """
    This class represents a generator which can be used to print an internal ast to a model in
    nest format.
    """
    renderer = None

    def __init__(self):
        # setup the environment
        self.renderer = TemplateRenderer()
        return

    def generateNESTModuleCode(self, _neurons):
        """Generates code that is necessary to integrate neuron models into the NEST infrastructure."""

        namespace = {'neurons': _neurons, 'moduleName': FrontendConfiguration.getModuleName()}
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(),
                                   FrontendConfiguration.getModuleName())) + '.h', 'w+') as f:
            f.write(self.renderer.render_module_header(namespace))
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(),
                                   FrontendConfiguration.getModuleName())) + '.cpp', 'w+') as f:
            f.write(self.renderer.render_module_class(namespace))
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(),
                                   'CMakeLists')) + '.txt', 'w+') as f:
            f.write(self.renderer.render_c_make_lists(namespace))
        if not os.path.isdir(os.path.realpath(os.path.join(FrontendConfiguration.getTargetPath(), 'sli'))):
            os.makedirs(os.path.realpath(os.path.join(FrontendConfiguration.getTargetPath(), 'sli')))
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(), 'sli',
                                   FrontendConfiguration.getModuleName() + "-init")) + '.sli', 'w+') as f:
            f.write(self.renderer.render_sli_init(namespace))
        code, message = Messages.getModuleGenerated(FrontendConfiguration.getTargetPath())
        Logger.logMessage(_neuron=None, _code=code, _message=message, _logLevel=LOGGING_LEVEL.INFO)
        return

    def analyseAndGenerateNeuron(self, _neuron):
        """Analysis a single neuron, solves it and generates the corresponding code."""
        code, message = Messages.getStartProcessingNeuron(_neuron.getName())
        Logger.logMessage(_neuron=_neuron, _errorPosition=_neuron.getSourcePosition(), _code=code, _message=message,
                          _logLevel=LOGGING_LEVEL.INFO)
        workingVersion = deepcopy(_neuron)
        # solve all equations
        workingVersion = self.solveOdesAndShapes(workingVersion)
        # update the symbol table
        ASTSymbolTableVisitor.update_symbol_table(workingVersion)
        self.generateNestCode(workingVersion)
        code, message = Messages.getCodeGenerated(_neuron.getName(), FrontendConfiguration.getTargetPath())
        Logger.logMessage(_neuron=_neuron, _errorPosition=_neuron.getSourcePosition(), _code=code, _message=message,
                          _logLevel=LOGGING_LEVEL.INFO)
        return

    def analyseAndGenerateNeurons(self, _neurons):
        for neuron in _neurons:
            self.analyseAndGenerateNeuron(neuron)
        return

    def generateModelHeader(self, _neuron):
        inputNeuronHeader = self.setupStandardNamespace(_neuron)
        outputNeuronHeader = self.renderer.render_neuron_header(inputNeuronHeader)
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(), _neuron.getName())) + '.h', 'w+') as f:
            f.write(outputNeuronHeader)
        return

    def generateModelImplementation(self, _neuron):
        inputNeuronImplementation = self.setupStandardNamespace(_neuron)
        outputNeuronImplementation = self.renderer.render_neuron_implementation(inputNeuronImplementation)
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(), _neuron.getName())) + '.cpp', 'w+') as f:
            f.write(outputNeuronImplementation)
        return

    def generateNestCode(self, _neuron):
        if not os.path.isdir(FrontendConfiguration.getTargetPath()):
            os.makedirs(FrontendConfiguration.getTargetPath())
        self.generateModelHeader(_neuron)
        self.generateModelImplementation(_neuron)
        return

    def setupStandardNamespace(self, _neuron):
        converter = NESTReferenceConverter(_usesGSL=False)
        legacyPrettyPrinter = LegacyExpressionPrinter(_reference_converter=converter)
        printer = NestPrinter(_expressionPrettyPrinter=legacyPrettyPrinter)
        gslConverter = GSLReferenceConverter()
        gslPrinter = LegacyExpressionPrinter(_reference_converter=gslConverter)
        namespace = {'neuronName': _neuron.getName(),
                     'neuron': _neuron,
                     'moduleName': FrontendConfiguration.getModuleName(),
                     'printer': printer,
                     'assignments': NestAssignmentsHelper(),
                     'names': NestNamesConverter(),
                     'declarations': NestDeclarationsHelper(),
                     'utils': ASTUtils(),
                     'idemPrinter': LegacyExpressionPrinter(),
                     'outputEvent': printer.printOutputEvent(_neuron.getBody()),
                     'isSpikeInput': ASTUtils.isSpikeInput(_neuron.getBody()),
                     'isCurrentInput': ASTUtils.isCurrentInput(_neuron.getBody()),
                     'odeTransformer': OdeTransformer(),
                     'printerGSL': gslPrinter}
        self.defineSolverType(namespace, _neuron)
        return namespace

    def defineSolverType(self, _namespace, _neuron):
        """For a handed over neuron this method enriches the namespace by methods which are used to solve
        odes."""
        _namespace['useGSL'] = False
        if _neuron.getEquationsBlocks() is not None and len(_neuron.getEquationsBlocks().getDeclarations()) > 0:
            if (not self.functionShapeExists(_neuron.getEquationsBlocks().getOdeShapes())) or \
                    len(_neuron.getEquationsBlocks().getOdeEquations()) > 1:
                _namespace['names'] = GSLNamesConverter()
                _namespace['useGSL'] = True
                converter = NESTReferenceConverter(_usesGSL=True)
                legacyPrettyPrinter = LegacyExpressionPrinter(_reference_converter=converter)
                _namespace['printer'] = NestPrinter(_expressionPrettyPrinter=legacyPrettyPrinter)
        return

    @classmethod
    def functionShapeExists(cls, _shapes):
        """For a handed over list of shapes this method checks if a single shape exits with differential order of 0."""
        for shape in _shapes:
            if isinstance(shape, ASTOdeShape) and shape.getVariable().getDifferentialOrder() == 0:
                return True
        return False

    @classmethod
    def solveOdesAndShapes(cls, _neuron):
        # it should be ensured that most one equations block is present
        equationsBlock = _neuron.getEquationsBlocks()
        if equationsBlock is None:
            return _neuron
        else:
            if len(equationsBlock.getOdeEquations()) > 1 and len(equationsBlock.getOdeShapes()) == 0:
                code, message = Messages.getNeuronSolvedBySolver(_neuron.getName())
                Logger.logMessage(_neuron=_neuron, _code=code, _message=message,
                                  _errorPosition=_neuron.getSourcePosition(), _logLevel=LOGGING_LEVEL.INFO)
                return _neuron
            else:
                code, message = Messages.getNeuronAnalyzed(_neuron.getName())
                Logger.logMessage(_neuron=_neuron, _code=code, _message=message,
                                  _errorPosition=_neuron.getSourcePosition(),
                                  _logLevel=LOGGING_LEVEL.INFO)
                workingCopy = EquationsBlockProcessor.solveOdeWithShapes(_neuron)
                return workingCopy
