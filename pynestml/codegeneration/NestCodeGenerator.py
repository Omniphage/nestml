#
# NestModuleGenerator.py
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
from pynestml.codegeneration.LoggingShortcuts import LoggingShortcuts
from pynestml.codegeneration.SolverOutputIntegrator import SolverOuptutIntegrator
from pynestml.codegeneration.target_files.CMakeLists import CMakeLists
from pynestml.codegeneration.target_files.ModuleHeader import ModuleHeader
from pynestml.codegeneration.target_files.ModuleImplementation import ModuleImplementation
from pynestml.codegeneration.target_files.NeuronHeader import NeuronHeader
from pynestml.codegeneration.target_files.NeuronImplementation import NeuronImplementation
from pynestml.codegeneration.target_files.SLIInit import SLIInit


class NestCodeGenerator(object):
    """Generates files for a nestml module and the corresponding neurons"""

    def __init__(self, _neurons):
        self.neurons = _neurons

    def generate(self):
        """Generates code that is necessary to integrate neuron models into the NEST infrastructure."""
        self.generate_nest_module_files()
        self.analyse_and_generate_neurons()
        LoggingShortcuts.log_finished_generating_module()
        return

    def generate_nest_module_files(self):
        ModuleHeader(self.neurons).generate()
        ModuleImplementation(self.neurons).generate()
        CMakeLists(self.neurons).generate()
        SLIInit(self.neurons).generate()

    def analyse_and_generate_neurons(self):
        for neuron in self.neurons:
            LoggingShortcuts.log_start_processing_neuron(neuron)
            self.analyse_and_generate_neuron(neuron)
            LoggingShortcuts.log_finished_processing_neuron(neuron)
        return

    @staticmethod
    def analyse_and_generate_neuron(_neuron):
        """Analyse a single neuron, solve it and generate the corresponding code."""
        solved_neuron = SolverOuptutIntegrator.integrate_solution_into_neuron(_neuron)
        NestCodeGenerator.generateNestCode(solved_neuron)
        return

    @staticmethod
    def generateNestCode(_neuron):
        NeuronHeader(_neuron).generate()
        NeuronImplementation(_neuron).generate()
        return
