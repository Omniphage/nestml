#
# IReferenceConverter.py
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
from abc import ABCMeta, abstractmethod

from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
from pynestml.modelprocessor.ASTVariable import ASTVariable


class IReferenceConverter(object):
    """
    This class represents a abstract super class for all possible reference converters, e.g. for nest, spinnacker
    or lems.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def convert_binary_op(self, _binary_operator):
        # type: (str) -> str
        pass

    @abstractmethod
    def convert_function_call(self, _ast_function_call):
        # type: (ASTFunctionCall) -> str
        pass

    @abstractmethod
    def convert_name_reference(self, _ast_variable):
        # type: (ASTVariable) -> str
        pass

    @abstractmethod
    def convert_constant(self, _constant_name):
        # type: (str) -> str
        pass

    @abstractmethod
    def convert_unary_op(self, _unary_operator):
        # type: (ASTUnaryOperator) -> str
        pass

    @abstractmethod
    def convert_encapsulated(self):
        # type: () -> str
        pass

    @abstractmethod
    def convert_logical_not(self):
        # type: () -> str
        pass

    @abstractmethod
    def convert_arithmetic_operator(self, _op):
        # type: (ASTArithmeticOperator) -> str
        pass

    @abstractmethod
    def convert_bit_operator(self, _op):
        # type: (ASTBitOperator) -> str
        pass

    @abstractmethod
    def convert_comparison_operator(self, _op):
        # type: (ASTComparisonOperator) -> str
        pass

    @abstractmethod
    def convert_logical_operator(self, _op):
        # type: (ASTLogicalOperator) -> str
        pass

    @abstractmethod
    def convert_ternary_operator(self):
        # type: () -> str
        pass
