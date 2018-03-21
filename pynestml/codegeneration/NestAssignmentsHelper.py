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

from pynestml.modelprocessor.VariableSymbol import VariableSymbol
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.modelprocessor.ASTAssignment import ASTAssignment
from pynestml.modelprocessor.Symbol import SymbolKind


class NestAssignmentsHelper(object):
    """
    This class contains several helper functions as used during printing of code.
    """

    @staticmethod
    def lhs_variable(_assignment):
        # type: (ASTAssignment) -> Union[None,VariableSymbol]
        symbol = _assignment.getScope().resolveToSymbol(_assignment.getVariable().getCompleteName(),
                                                        SymbolKind.VARIABLE)
        if symbol is not None:
            return symbol
        else:
            Logger.logMessage('No symbol could be resolved!', LOGGING_LEVEL.ERROR)
            return

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
        symbol = _assignment.getScope().resolveToSymbol(_assignment.getVariable().getCompleteName(),
                                                        SymbolKind.VARIABLE)
        if symbol is not None:
            if symbol.hasVectorParameter():
                return True
            else:
                # otherwise we have to check if one of the variables used in the rhs is a vector
                for var in _assignment.getExpression().getVariables():
                    symbol = var.getScope().resolveToSymbol(var.getCompleteName(), SymbolKind.VARIABLE)
                    if symbol is not None and symbol.hasVectorParameter():
                        return True
                return False
        else:
            Logger.logMessage('No symbol could be resolved!', LOGGING_LEVEL.ERROR)
            return False

    @staticmethod
    def print_size_parameter(_assignment):
        # type: (ASTAssignment) -> VariableSymbol
        vector_variable = None
        for variable in _assignment.getExpression().getVariables():
            symbol = variable.getScope().resolveToSymbol(variable.getCompleteName(), SymbolKind.VARIABLE)
            if symbol is not None and symbol.hasVectorParameter():
                vector_variable = symbol
                break
        if vector_variable is None:
            vector_variable = _assignment.getScope(). \
                resolveToSymbol(_assignment.getVariable().getCompleteName(), SymbolKind.VARIABLE)
        # this function is called only after the corresponding assignment has been tested for been a vector
        return vector_variable.getVectorParameter()
