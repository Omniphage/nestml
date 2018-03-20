#
# IdempotentReferenceConverter.py
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

from pynestml.codegeneration.IReferenceConverter import IReferenceConverter
from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.utils.ASTUtils import ASTUtils


class IdempotentReferenceConverter(IReferenceConverter):
    """Returns the same input as output, i.e., an identity mapping of elements is preformed."""

    def convert_unary_op(self, _unary_operator):
        # type: (ASTUnaryOperator) -> str
        return str(_unary_operator) + '%s'

    def convert_name_reference(self, _ast_variable):
        # type: (ASTVariable) -> str
        return _ast_variable.getCompleteName()

    def convert_function_call(self, _ast_function_call):
        # type: (ASTFunctionCall) -> str
        result = _ast_function_call.getName()
        if ASTUtils.needsArguments(_ast_function_call):
            result += '(%s)'
        else:
            result += '()'
        return result

    def convert_binary_op(self, _binary_operator):
        # type: (Union[ASTArithmeticOperator,ASTBitOperator,ASTComparisonOperator,ASTLogicalOperator]) -> str
        return '%s' + str(_binary_operator) + '%s'

    def convert_constant(self, _constant_name):
        # type: (str) -> str
        return _constant_name

    def convert_ternary_operator(self):
        # type: () -> str
        return '(' + '%s' + ')?(' + '%s' + '):(' + '%s' + ')'

    def convert_logical_operator(self, _op):
        # type: (ASTLogicalOperator) -> str
        return str(_op)

    def convert_arithmetic_operator(self, _op):
        # type: (ASTArithmeticOperator) -> str
        return str(_op)

    def convert_encapsulated(self):
        # type: () -> str
        return '(%s)'

    def convert_comparison_operator(self, _op):
        # type: (ASTComparisonOperator) -> str
        return str(_op)

    def convert_logical_not(self):
        # type: () -> str
        return 'not %s'

    def convert_bit_operator(self, _op):
        # type: (ASTBitOperator) -> str
        return str(_op)
