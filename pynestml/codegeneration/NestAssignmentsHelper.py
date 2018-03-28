#
# NestAssignmentsHelper.py
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
from typing import Union

from pynestml.codegeneration.LoggingShortcuts import LoggingShortcuts
from pynestml.modelprocessor.ASTAssignment import ASTAssignment
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.modelprocessor.Scope import CannotResolveSymbolError
from pynestml.modelprocessor.VariableSymbol import VariableSymbol


class NestAssignmentsHelper(object):
    """
    This class contains several helper functions as used during printing of code.
    """

    @staticmethod
    def lhs_variable(_assignment):
        # type: (ASTAssignment) -> Union[None,VariableSymbol]
        try:
            return _assignment.getScope().resolve_variable_symbol(_assignment.getVariable().getCompleteName())
        except CannotResolveSymbolError:
            LoggingShortcuts.log_could_not_resolve(_assignment.getVariable().getCompleteName(),
                                                   _assignment.getVariable())

    @staticmethod
    def print_assignments_operation(_assignment):
        # type: (ASTAssignment) -> str
        if _assignment.isCompoundSum():
            return '+='
        elif _assignment.isCompoundMinus():
            return '-='
        elif _assignment.isCompoundProduct():
            return '*='
        elif _assignment.isCompoundQuotient():
            return '/='
        else:
            return '='

    @staticmethod
    def is_vectorized_assignment(_assignment):
        # type: (ASTAssignment) -> bool
        for var in _assignment.getExpression().getVariables():
            if NestAssignmentsHelper.variable_has_vector_parameter(var):
                return True
        return False

    @staticmethod
    def variable_has_vector_parameter(_variable):
        # type: (ASTVariable) -> bool
        try:
            symbol = _variable.getScope().resolve_variable_symbol(_variable.getCompleteName())
            if symbol.hasVectorParameter():
                return True
        except CannotResolveSymbolError:
            LoggingShortcuts.log_could_not_resolve(_variable.getCompleteName(), _variable)
            return False

    @staticmethod
    def print_size_parameter(_assignment):
        # type: (ASTAssignment) -> VariableSymbol
        vector_variable = None
        for variable in _assignment.getExpression().getVariables():
            try:
                symbol = variable.getScope().resolve_variable_symbol(variable.getCompleteName())
                if symbol.hasVectorParameter():
                    vector_variable = symbol
                    break
            except CannotResolveSymbolError:
                LoggingShortcuts.log_could_not_resolve(variable.getCompleteName(), variable)

        if vector_variable is None:
            vector_variable = _assignment.getScope().resolve_variable_symbol(
                _assignment.getVariable().getCompleteName())
        # this function is called only after the corresponding assignment has been tested for been a vector
        return vector_variable.getVectorParameter()
