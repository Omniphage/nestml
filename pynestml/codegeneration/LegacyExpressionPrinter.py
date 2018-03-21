#
# LegacyExpressionPrinter.py
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

from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression


class LegacyExpressionPrinter(ExpressionsPrettyPrinter):
    """
    An adjusted version of the pretty printer which does not print units with literals.
    """

    def _do_print(self, _expr=None):
        # type: (Union[ASTExpression,ASTSimpleExpression]) -> str
        if isinstance(_expr, ASTSimpleExpression):
            if _expr.isNumericLiteral():
                return self._types_printer.pretty_print(_expr.getNumericLiteral())

        return super(LegacyExpressionPrinter, self)._do_print(_expr)
