#
# GSLNamesConverter.py
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
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.modelprocessor.VariableSymbol import VariableSymbol


class GSLNamesConverter(object):
    """
    A GSL names converter as use to transform names to GNU Scientific Library.
    """

    @classmethod
    def array_index(cls, _variable_symbol):
        # type: (VariableSymbol) -> str
        """Transforms the haded over symbol to a GSL processable format."""
        return 'State_::' + NestNamesConverter.convertToCPPName(_variable_symbol.getSymbolName())

    @classmethod
    def name(cls, _variable_symbol):
        # type: (VariableSymbol) -> str
        """Transforms the haded over symbol to a GSL processable format."""
        if _variable_symbol.isInitValues() and not _variable_symbol.isFunction():
            return 'ode_state[State_::' + NestNamesConverter.convertToCPPName(_variable_symbol.getSymbolName()) + ']'
        else:
            return NestNamesConverter.name(_variable_symbol)

    @classmethod
    def getter(cls, _variable_symbol):
        # type: (VariableSymbol) -> str
        """Converts for a handed over symbol the corresponding name of the getter to a gsl processable format."""
        return NestNamesConverter.getter(_variable_symbol)

    @classmethod
    def setter(cls, _variable_symbol):
        # type: (VariableSymbol) -> str
        """Converts for a handed over symbol the corresponding name of the setter to a gsl processable format."""
        return NestNamesConverter.setter(_variable_symbol)

    @classmethod
    def buffer_value(cls, _variable_symbol):
        # type: (VariableSymbol) -> str
        """Converts for a handed over symbol the corresponding name of the buffer to a gsl processable format."""
        return NestNamesConverter.bufferValue(_variable_symbol)

    @classmethod
    def convert_to_cpp_name(cls, _variable_name):
        # type: (str) -> str
        """Converts a handed over name to the corresponding gsl / c++ naming guideline."""
        return NestNamesConverter.convertToCPPName(_variable_name)
