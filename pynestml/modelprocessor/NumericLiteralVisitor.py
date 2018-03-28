#
# NumericLiteralVisitor.py
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
simpleExpression : (INTEGER|FLOAT) (variable)?
"""

from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes


class NumericLiteralVisitor(NESTMLVisitor):
    """
    Visits a single numeric literal and updates its type.
    """

    def visit_simple_expression(self, _expr=None):
        # type: (ASTSimpleExpression) -> None
        assert _expr.getScope() is not None, "Run symboltable creator."
        # if variable is also set in this expression, the var type overrides the literal
        if _expr.getVariable() is not None:
            var_name = _expr.getVariable().getName()
            variable_symbol_resolve = _expr.getScope().resolve_variable_symbol(var_name)
            _expr.type = variable_symbol_resolve.getTypeSymbol()
            _expr.type.referenced_object = _expr
            return

        if _expr.getNumericLiteral() is not None and isinstance(_expr.getNumericLiteral(), float):
            _expr.type = PredefinedTypes.getRealType()
            _expr.type.referenced_object = _expr
            return

        elif _expr.getNumericLiteral() is not None and isinstance(_expr.getNumericLiteral(), int):
            _expr.type = PredefinedTypes.getIntegerType()
            _expr.type.referenced_object = _expr
            return
