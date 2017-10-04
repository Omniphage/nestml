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
from jinja2 import Template, Environment, FileSystemLoader, PackageLoader
from pynestml.nestml.ASTNeuron import ASTNeuron
from pynestml.frontend.FrontendConfiguration import FrontendConfiguration
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
import os


class NestCodeGenerator(object):
    """
    This class represents a generator which can be used to print an internal ast to a model in
    nest format.
    """
    __templateCMakeLists = None
    __templateModuleClass = None
    __templateModuleHeader = None
    __templateNeuronHeader = None
    __templateNeuronImplementation = None

    def __init__(self):
        """
        Standard constructor to init the generator.
        """
        # setup the environment
        env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templatesNEST')))
        # setup the cmake template
        """
        with open(os.path.join(os.path.dirname(__file__), 'templatesNEST', 'CMakeLists.html'),
                  'r') as templateCMakeLists:
            data = templateCMakeLists.read()
            self.__templateCMakeLists = Template(data)
        """
        # setup the module class template
        """
        with open(os.path.join(os.path.dirname(__file__), 'templatesNEST', 'ModuleClass.html'),
                  'r') as templateModuleClass:
            data = templateModuleClass.read()
            self.__templateModuleClass = Template(data)
        """
        # setup the module header
        """
        with open(os.path.join(os.path.dirname(__file__), 'templatesNEST', 'ModuleHeader.html'),
                  'r') as templateModuleHeader:
            data = templateModuleHeader.read()
            self.__templateModuleHeader = Template(data)
        """
        # setup the neuron header template
        self.__templateNeuronHeader = env.get_template('NeuronHeader.html')
        # setup the neuron implementation template
        self.__templateNeuronImplementation = env.get_template('NeuronClass.html')
        return

    def generateModels(self, _modelRoots=None):
        """
        Generates the corresponding model for the handed over neuron
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_modelRoots is not None and isinstance(_modelRoots, list)), \
            '(PyNestML.Backend.NEST) No or wrong type of roots list provided (%s)!' % type(_modelRoots)
        # first generate the cmake file
        """
        inputMakeLists = {}
        outputMakeLists = self.__templateCMakeLists.render(inputMakeLists)
        
        # now the class
        inputModuleClass = {'moduleName': 'TODO', 'neurons': list()}
        outputModuleClass = self.__templateModuleClass.render(inputModuleClass)
        # now the header
        
        inputModuleHeader = {}
        outputModuleHeader = self.__templateModuleHeader.render(inputModuleHeader)
        """
        # finally print everthing
        # first the cmake file
        """
        if not os.path.isdir(FrontendConfiguration.getTargetPath()):
            os.makedirs(FrontendConfiguration.getTargetPath())
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(), CMakeLists)) + '.cpp', 'w+') as f:
            f.write(str(outputMakeLists))
        """
        # now the class
        """
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(), 'TODO2')) + '.cpp', 'w+') as f:
            f.write(str(outputModuleClass))
        # now the header
        
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(), 'TODO3')) + '.h', 'w+') as f:
            f.write(str(outputModuleHeader))
        """
        return

    def generateModuleHeader(self, _moduleName=None):
        """
        Generates the header of the handed over module.
        :param _moduleName: the name of the module
        :type _moduleName: str
        """
        assert (_moduleName is not None and isinstance(_moduleName, str)), \
            '(PyNestML.CodeGenerator.NEST) No or wrong type of module name provided (%s)!' % type(_moduleName)
        if not os.path.isdir(FrontendConfiguration.getTargetPath()):
            os.makedirs(FrontendConfiguration.getTargetPath())
        inputModuleHeader = {'moduleName': 'TODO'}
        outputModuleHeader = self.__templateModuleHeader.render(inputModuleHeader)
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(), _moduleName)) + '.h', 'w+') as f:
            f.write(str(outputModuleHeader))
        return

    def generateModuleClass(self, _neurons=list(), _moduleName=None):
        """
        Generates the class of the handed over module.
        :param _neurons: a list of neurons
        :type _neurons: list(ASTNeuron)
        :param _moduleName: the name of the module
        :type _moduleName: str
        """
        assert (_moduleName is not None and isinstance(_moduleName, str)), \
            '(PyNestML.CodeGenerator.NEST) No or wrong type of module name provided (%s)!' % type(_moduleName)
        if not os.path.isdir(FrontendConfiguration.getTargetPath()):
            os.makedirs(FrontendConfiguration.getTargetPath())
        inputModuleClass = {'moduleName': 'TODO', 'neurons': _neurons}
        outputModuleClass = self.__templateModuleClass.render(inputModuleClass)
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(), _moduleName)) + '.cpp', 'w+') as f:
            f.write(str(outputModuleClass))
        return

    def generateNESTModuleCode(self, _modelRoots=list(), _moduleName=None):
        """
        Generates the complete nest module code.
        :param _modelRoots: a list of NESTMLCompilationUnits
        :type _modelRoots: list(ASTNestmlCompilationUnit)
        :param _moduleName: the name of the module
        :type _moduleName: str
        """
        assert (_modelRoots is not None and isinstance(_modelRoots, list)), \
            '(PyNestML.CodeGenerator.NEST) No or wrong type of model roots provided (%s)!' % type(_modelRoots)
        assert (_moduleName is not None and isinstance(_moduleName, str)), \
            '(PyNestML.CodeGenerator.NEST) No or wrong type of module name provided (%s)!' % type(_moduleName)

        self.generateModuleHeader(_moduleName)
        #self.generateModuleClass(_)

    def generateHeader(self, _neuron=None):
        """
        For a handed over neuron, this method generates the corresponding header file.
        :param _neuron: a single neuron object.
        :type _neuron:  ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CodeGenerator.NEST) No or wrong type of neuron provided (%s)!' % type(_neuron)
        inputNeuronHeader = self.setupStandardNamespace(_neuron)
        outputNeuronHeader = self.__templateNeuronHeader.render(inputNeuronHeader)
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(), _neuron.getName())) + '.h', 'w+') as f:
            f.write(str(outputNeuronHeader))
        return

    def generateClassImplementation(self, _neuron=None):
        """
        For a handed over neuron, this method generates the corresponding implementation file.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CodeGenerator.NEST) No or wrong type of neuron provided (%s)!' % type(_neuron)
        inputNeuronImplementation = self.setupStandardNamespace(_neuron)
        outputNeuronImplementation = self.__templateNeuronImplementation.render(inputNeuronImplementation)
        with open(str(os.path.join(FrontendConfiguration.getTargetPath(), _neuron.getName())) + '.cpp', 'w+') as f:
            f.write(str(outputNeuronImplementation))
        return

    def generateNestCode(self, _neuron=None):
        """
        For a handed over neuron, this method generates the corresponding header and implementation file.
        :param _neuron: a single neuron object.
        :type _neuron: ASTNeuron
        """
        if not os.path.isdir(FrontendConfiguration.getTargetPath()):
            os.makedirs(FrontendConfiguration.getTargetPath())
        Logger.logMessage('Start generating header for %s...' % _neuron.getName(), LOGGING_LEVEL.INFO)
        self.generateHeader(_neuron)
        Logger.logMessage('Start generating implementation for %s...' % _neuron.getName(), LOGGING_LEVEL.INFO)
        self.generateClassImplementation(_neuron)
        return

    def setupStandardNamespace(self, _neuron=None):
        """
        Returns a standard namespace with often required functionality.
        :param _neuron: a single neuron instance
        :type _neuron: ASTNeuron
        :return: a map from name to functionality.
        :rtype: dict
        """
        from pynestml.codegeneration.NestDeclarationsHelper import NestDeclarationsHelper
        from pynestml.codegeneration.NestAssignmentsHelper import NestAssignmentsHelper
        from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
        from pynestml.codegeneration.NestPrinter import NestPrinter
        from pynestml.utils.OdeTransformer import OdeTransformer
        from pynestml.utils.ASTUtils import ASTUtils
        namespace = {}
        namespace['neuronName'] = _neuron.getName()
        namespace['neuron'] = _neuron
        namespace['moduleName'] = 'TODO module name'
        # helper classes and objects
        namespace['printer'] = NestPrinter()
        namespace['assignments'] = NestAssignmentsHelper()
        namespace['names'] = NestNamesConverter()
        namespace['declarations'] = NestDeclarationsHelper()
        namespace['utils'] = ASTUtils
        # information regarding the neuron
        namespace['outputEvent'] = namespace['printer'].printOutputEvent(_neuron.getBody())
        namespace['isSpikeInput'] = ASTUtils.isSpikeInput(_neuron.getBody())
        namespace['isCurrentInput'] = ASTUtils.isCurrentInput(_neuron.getBody())
        # some additional information
        namespace['useGSL'] = False  # Todo
        namespace['odeTransformer'] = OdeTransformer()
        # todo more
        return namespace

    def test(self, _neuron):
        with open(os.path.join(os.path.dirname(__file__), 'templatesNEST', 'spl', 'ModuleClass.html'),
                  'r') as templateModuleClass:
            data = templateModuleClass.read()
            templateModuleClass = Template(data)
            inputModuleClass = self.setupStandardNamespace(_neuron)
            outputModuleClass = templateModuleClass.render(inputModuleClass)
            with open(str(os.path.join(FrontendConfiguration.getTargetPath(), 'teeest')) + '.cpp', 'w+') as f:
                f.write(str(outputModuleClass))