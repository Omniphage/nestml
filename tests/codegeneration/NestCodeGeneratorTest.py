#
# NestCodeGeneratorTest.py
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
import unittest

from mock import Mock, MagicMock, patch, call

from pynestml.codegeneration.NestCodeGenerator import NestCodeGenerator
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.utils.Logger import Logger, LOGGING_LEVEL

patch.object = patch.object


# noinspection PyMissingTypeHints,PyTypeChecker
class NestCodeGeneratorTest(unittest.TestCase):
    class_under_test = None
    mock_neurons = None

    logging_shortcuts = 'pynestml.codegeneration.NestCodeGenerator.LoggingShortcuts'
    module_implementation = 'pynestml.codegeneration.NestCodeGenerator.ModuleImplementation'
    module_header = 'pynestml.codegeneration.NestCodeGenerator.ModuleHeader'
    c_make_lists = 'pynestml.codegeneration.NestCodeGenerator.CMakeLists'
    sli_init = 'pynestml.codegeneration.NestCodeGenerator.SLIInit'
    neuron_header = 'pynestml.codegeneration.NestCodeGenerator.NeuronHeader'
    neuron_implementation = 'pynestml.codegeneration.NestCodeGenerator.NeuronImplementation'
    solver_output_integrator = 'pynestml.codegeneration.NestCodeGenerator.SolverOutputIntegrator'

    # noinspection PyPep8Naming
    def setUp(self):
        self.mock_neurons = [Mock(ASTNeuron)]
        self.class_under_test = NestCodeGenerator(self.mock_neurons)
        Logger.initLogger(LOGGING_LEVEL.INFO)

    def test_init_with_neuron_list(self):
        self.assertEqual(self.class_under_test.neurons, self.mock_neurons)

    def test_generate_calls_generate_module_files(self):
        self.class_under_test.generate_nest_module_files = MagicMock()
        self.class_under_test.analyse_and_generate_neurons = MagicMock()
        with patch(self.logging_shortcuts):
            self.class_under_test.generate()
        self.class_under_test.generate_nest_module_files.assert_called()

    def test_generate_calls_analyse_and_generate(self):
        self.class_under_test.generate_nest_module_files = MagicMock()
        self.class_under_test.analyse_and_generate_neurons = MagicMock()
        with patch(self.logging_shortcuts):
            self.class_under_test.generate()
        self.class_under_test.analyse_and_generate_neurons.assert_called()

    def test_generate_nest_module_files_generates_module_header(self):
        with patch(self.module_implementation), patch(self.module_header) as mock_module_header, patch(
                self.c_make_lists), patch(self.sli_init):
            self.class_under_test.generate_nest_module_files()
            mock_module_header.return_value.generate.assert_called()

    def test_generate_nest_module_files_generates_module_implementation(self):
        with patch(self.module_implementation)as mock_module_implementation, patch(self.module_header), patch(
                self.c_make_lists), patch(self.sli_init):
            self.class_under_test.generate_nest_module_files()
            mock_module_implementation.return_value.generate.assert_called()

    def test_generate_nest_module_files_generates_c_make_lists(self):
        with patch(self.module_implementation), patch(self.module_header), patch(
                self.c_make_lists) as mock_c_make_lists, patch(self.sli_init):
            self.class_under_test.generate_nest_module_files()
            mock_c_make_lists.return_value.generate.assert_called()

    def test_generate_nest_module_files_generates_sli_init(self):
        with patch(self.module_implementation), patch(self.module_header), patch(
                self.c_make_lists) as mock_c_make_lists, patch(self.sli_init) as mock_sli_init:
            self.class_under_test.generate_nest_module_files()
            mock_sli_init.return_value.generate.assert_called()

    def test_analyse_and_generate_neurons_calls_analyse_and_generate_for_each_neuron(self):
        neuron1 = Mock(ASTNeuron)
        neuron2 = Mock(ASTNeuron)
        self.class_under_test.neurons = [neuron1, neuron2]
        self.class_under_test.analyse_and_generate_neuron = Mock()
        with patch(self.logging_shortcuts):
            self.class_under_test.analyse_and_generate_neurons()
        calls = [call(neuron1), call(neuron2)]
        self.class_under_test.analyse_and_generate_neuron.assert_has_calls(calls)

    def test_analyse_and_generate_neuron_solves_odes(self):
        neuron = Mock(ASTNeuron)
        with patch(self.solver_output_integrator)as mock_solver_integrator, patch.object(NestCodeGenerator,
                                                                                         'generate_nest_code'):
            self.class_under_test.analyse_and_generate_neuron(neuron)
            mock_solver_integrator.integrate_solution_into_neuron.assert_called()

    def test_analyse_and_generate_neuron_generates_nest_code(self):
        neuron = Mock(ASTNeuron)
        with patch(self.solver_output_integrator), patch.object(NestCodeGenerator, 'generate_nest_code'):
            self.class_under_test.analyse_and_generate_neuron(neuron)
            # noinspection PyUnresolvedReferences
            self.class_under_test.generate_nest_code.assert_called()

    def test_generate_nest_code_generates_neuron_header(self):
        neuron = Mock(ASTNeuron)
        with patch(self.neuron_header)as mock_neuron_header, patch(self.neuron_implementation):
            self.class_under_test.generate_nest_code(neuron)
            mock_neuron_header.return_value.generate.assert_called()

    def test_generate_nest_code_generates_neuron_implementation(self):
        neuron = Mock(ASTNeuron)
        with patch(self.neuron_header), patch(self.neuron_implementation)as mock_neuron_impl:
            self.class_under_test.generate_nest_code(neuron)
            mock_neuron_impl.return_value.generate.assert_called()
