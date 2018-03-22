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
from abc import ABCMeta, abstractmethod
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


class TemplateCollection(object):
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templatesNEST')))
    c_make_lists = env.get_template('CMakeLists.jinja2')
    module_implementation = env.get_template('ModuleClass.jinja2')
    module_header = env.get_template('ModuleHeader.jinja2')
    sli_init = env.get_template('SLI_Init.jinja2')
    neuron_header = env.get_template('NeuronHeader.jinja2')
    neuron_implementation = env.get_template('NeuronClass.jinja2')


class TargetPaths(object):
    def __init__(self):
        self.sli_directory = os.path.join(FrontendConfiguration.getTargetPath(), 'sli')
        self.module_header_path = os.path.join(FrontendConfiguration.getTargetPath(),
                                               FrontendConfiguration.getModuleName()) + '.h'
        self.module_implementation_path = os.path.join(FrontendConfiguration.getTargetPath(),
                                                       FrontendConfiguration.getModuleName()) + '.cpp'
        self.c_make_lists_path = os.path.join(FrontendConfiguration.getTargetPath(), 'CMakeLists') + '.txt'
        self.sli_init_path = os.path.join(FrontendConfiguration.getTargetPath(), 'sli',
                                          FrontendConfiguration.getModuleName() + "-init") + '.sli'
        self.neuron_header_path = os.path.join(FrontendConfiguration.getTargetPath(), '%s.h')
        self.neuron_implementation_path = os.path.join(FrontendConfiguration.getTargetPath(), '%s.cpp')


class TargetFile(object):
    __metaclass__ = ABCMeta

    def __init__(self, _path, _template):
        self.path = _path
        self.template = _template

    def generate(self):
        with open(self.path, 'w+') as file:
            file.write(self.template.render(self.setup_namespace()))

    @abstractmethod
    def setup_namespace(self):
        pass


class ModuleLevelFile(TargetFile):
    def __init__(self, _neurons, _path, _template):
        super(ModuleLevelFile, self).__init__(_path, _template)
        self.neurons = _neurons

    def setup_namespace(self):
        return {'neurons': self.neurons, 'moduleName': FrontendConfiguration.getModuleName()}


class ModuleHeader(ModuleLevelFile):
    def __init__(self, _neurons):
        super(ModuleHeader, self).__init__(_neurons,
                                           TargetPaths().module_header_path,
                                           TemplateCollection.module_header)


class ModuleImplementation(ModuleLevelFile):
    def __init__(self, _neurons):
        super(ModuleImplementation, self).__init__(_neurons,
                                                   TargetPaths().module_implementation_path,
                                                   TemplateCollection.module_implementation)


class CMakeLists(ModuleLevelFile):
    def __init__(self, _neurons):
        super(CMakeLists, self).__init__(_neurons,
                                         TargetPaths().c_make_lists_path,
                                         TemplateCollection.c_make_lists)


class SLIInit(ModuleLevelFile):
    def __init__(self, _neurons):
        self.create_sli_directory()
        super(SLIInit, self).__init__(_neurons,
                                      TargetPaths().sli_init_path,
                                      TemplateCollection.sli_init)

    @staticmethod
    def create_sli_directory():
        sli_directory_path = os.path.realpath(TargetPaths().sli_directory)
        if not os.path.isdir(sli_directory_path):
            os.makedirs(sli_directory_path)


class NeuronFile(TargetFile):
    def __init__(self, _neuron, _path, _template):
        super(NeuronFile, self).__init__(_path % _neuron.getName(),
                                         _template)
        self.neuron = _neuron

    def setup_namespace(self):
        converter = NESTReferenceConverter(_usesGSL=False)
        legacyPrettyPrinter = LegacyExpressionPrinter(_reference_converter=converter)
        printer = NestPrinter(_expressionPrettyPrinter=legacyPrettyPrinter)
        gslConverter = GSLReferenceConverter()
        gslPrinter = LegacyExpressionPrinter(_reference_converter=gslConverter)
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
                     'printerGSL': gslPrinter}
        self.defineSolverType(namespace, self.neuron)
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


class NeuronHeader(NeuronFile):

    def __init__(self, _neuron):
        super(NeuronHeader, self).__init__(_neuron,
                                           TargetPaths().neuron_header_path,
                                           TemplateCollection.neuron_header)


class NeuronImplementation(NeuronFile):

    def __init__(self, _neuron):
        super(NeuronImplementation, self).__init__(_neuron,
                                                   TargetPaths().neuron_implementation_path,
                                                   TemplateCollection.neuron_implementation)


class NestCodeGenerator(object):
    """
    This class represents a generator which can be used to print an internal ast to a model in
    nest format.
    """

    def generateNESTModuleCode(self, _neurons):
        """Generates code that is necessary to integrate neuron models into the NEST infrastructure."""
        self.generate_nest_module_files(_neurons)
        code, message = Messages.getModuleGenerated(FrontendConfiguration.getTargetPath())
        Logger.logMessage(_neuron=None, _code=code, _message=message, _logLevel=LOGGING_LEVEL.INFO)
        return

    @staticmethod
    def generate_nest_module_files(_neurons):
        ModuleHeader(_neurons).generate()
        ModuleImplementation(_neurons).generate()
        CMakeLists(_neurons).generate()
        SLIInit(_neurons).generate()

    def analyseAndGenerateNeurons(self, _neurons):
        for neuron in _neurons:
            self.analyseAndGenerateNeuron(neuron)
        return

    def analyseAndGenerateNeuron(self, _neuron):
        """Analyse a single neuron, solve it and generate the corresponding code."""
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

    def generateNestCode(self, _neuron):
        if not os.path.isdir(FrontendConfiguration.getTargetPath()):
            os.makedirs(FrontendConfiguration.getTargetPath())
        NeuronHeader(_neuron).generate()
        NeuronImplementation(_neuron).generate()
        return
