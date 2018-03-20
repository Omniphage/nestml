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

from mock import patch, Mock

from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.modelprocessor.VariableSymbol import VariableSymbol


# noinspection PyTypeChecker
@patch('pynestml.codegeneration.GSLNamesConverter.NestNamesConverter')
class GSLNamesConverterTest(unittest.TestCase):
    class_under_test = GSLNamesConverter()

    def test_array_index(self, _mock_nestml_names_converter):
        # type: () -> None
        _mock_nestml_names_converter.convertToCPPName.return_value = 'varfoo'
        result = self.class_under_test.array_index(Mock())
        self.assertEqual('State_::varfoo', result)

    def test_name_with_regular_variable_symbol(self, _mock_nestml_names_converter):
        # type: () -> None
        _mock_nestml_names_converter.name.return_value = 'varfoo'
        result = self.class_under_test.name(Mock())
        self.assertEqual('varfoo', result)

    def test_name_with_initial_value(self, _mock_nestml_names_converter):
        # type: () -> None
        _mock_nestml_names_converter.convertToCPPName.return_value = 'varfoo'
        mock_var_symbol = Mock(VariableSymbol)
        mock_var_symbol.isInitValues.return_value = True
        mock_var_symbol.isFunction.return_value = False
        result = self.class_under_test.name(mock_var_symbol)
        self.assertEqual('ode_state[State_::varfoo]', result)

    def test_getter(self, _mock_nestml_names_converter):
        # type: () -> None
        _mock_nestml_names_converter.getter.return_value = 'get_varfoo'
        result = self.class_under_test.getter(Mock())
        self.assertEqual('get_varfoo', result)

    def test_setter(self, _mock_nestml_names_converter):
        # type: () -> None
        _mock_nestml_names_converter.setter.return_value = 'set_varfoo'
        result = self.class_under_test.setter(Mock())
        self.assertEqual('set_varfoo', result)

    def test_buffer_value(self, _mock_nestml_names_converter):
        # type: () -> None
        _mock_nestml_names_converter.bufferValue.return_value = 'buffer_value_called'
        result = self.class_under_test.buffer_value(Mock())
        self.assertEqual('buffer_value_called', result)

    def test_convert_to_cpp_name(self, _mock_nestml_names_converter):
        # type: () -> None
        _mock_nestml_names_converter.convertToCPPName.return_value = 'cpp_name_called'
        result = self.class_under_test.convert_to_cpp_name('mock')
        self.assertEqual('cpp_name_called', result)
