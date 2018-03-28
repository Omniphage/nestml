#
# VariableVisitor.py
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

"""
simpleExpression : variable
"""
from copy import copy

from pynestml.codegeneration.LoggingShortcuts import LoggingShortcuts
from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
from pynestml.modelprocessor.Scope import CannotResolveSymbolError
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import MessageCode


class VariableVisitor(NESTMLVisitor):
    """
    This visitor visits a single variable and updates its type.
    """

    def visit_simple_expression(self, _expr=None):
        # type: (ASTSimpleExpression) -> None
        scope = _expr.getScope()
        var_name = _expr.getVariable().getName()
        try:
            var_resolve = scope.resolve_variable_symbol(var_name)
            _expr.type = var_resolve.getTypeSymbol()
            _expr.type.referenced_object = _expr
        except CannotResolveSymbolError:
            LoggingShortcuts.log_could_not_resolve(var_name,_expr.getVariable())
            _expr.type = ErrorTypeSymbol()
        return