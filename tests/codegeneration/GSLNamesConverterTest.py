#
# GSLNamesConverterTest.py
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

from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.VariableSymbol import VariableSymbol, BlockType, VariableType

PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedVariables.registerPredefinedVariables()
PredefinedFunctions.registerPredefinedFunctions()


class GSLNamesConverterTest(unittest.TestCase):
    gsl_names_converter = GSLNamesConverter()

    def test_array_index(self):
        # type: () -> None
        var_symbol = VariableSymbol(_blockType=BlockType.EQUATION, _name='varfoo',
                                    _typeSymbol=PredefinedTypes.getRealType(), _variableType=VariableType.EQUATION)
        result = self.gsl_names_converter.array_index(var_symbol)
        self.assertEqual('State_::varfoo', result)

    def test_name_with_regular_variable_symbol(self):
        # type: () -> None
        var_symbol = VariableSymbol(_blockType=BlockType.EQUATION, _name='varfoo',
                                    _typeSymbol=PredefinedTypes.getRealType(), _variableType=VariableType.EQUATION)
        result = self.gsl_names_converter.name(var_symbol)
        self.assertEqual('varfoo', result)

    def test_name_with_initial_value(self):
        # type: () -> None
        var_symbol = VariableSymbol(_blockType=BlockType.INITIAL_VALUES, _name='varfoo',
                                    _typeSymbol=PredefinedTypes.getRealType(), _variableType=VariableType.EQUATION)
        result = self.gsl_names_converter.name(var_symbol)
        self.assertEqual('ode_state[State_::varfoo]', result)

    def test_getter(self):
        # type: () -> None
        var_symbol = VariableSymbol(_blockType=BlockType.INITIAL_VALUES, _name='varfoo',
                                    _typeSymbol=PredefinedTypes.getRealType(), _variableType=VariableType.EQUATION)
        result = self.gsl_names_converter.getter(var_symbol)
        self.assertEqual('get_varfoo', result)

    def test_setter(self):
        # type: () -> None
        var_symbol = VariableSymbol(_blockType=BlockType.INITIAL_VALUES, _name='varfoo',
                                    _typeSymbol=PredefinedTypes.getRealType(), _variableType=VariableType.EQUATION)
        result = self.gsl_names_converter.setter(var_symbol)
        self.assertEqual('set_varfoo', result)

    def test_buffer_value(self):
        # type: () -> None
        var_symbol = VariableSymbol(_blockType=BlockType.INITIAL_VALUES, _name='varfoo',
                                    _typeSymbol=PredefinedTypes.getRealType(), _variableType=VariableType.EQUATION)
        result = self.gsl_names_converter.buffer_value(var_symbol)
        self.assertEqual('varfoo_grid_sum_', result)

    def test_convert_to_cpp_name(self):
        # type: () -> None
        result = self.gsl_names_converter.convert_to_cpp_name('varfoo')
        self.assertEqual('varfoo', result)
