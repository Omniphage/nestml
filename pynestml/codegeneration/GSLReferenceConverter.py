#
# GSLReferenceConverterTest.py
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

from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.codegeneration.IReferenceConverter import IReferenceConverter
from pynestml.codegeneration.NestReferenceConverter import NESTReferenceConverter
from pynestml.codegeneration.UnitConverter import UnitConverter
from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.Symbol import SymbolKind


class GSLReferenceConverter(IReferenceConverter):
    """
    This class is used to convert operators and constant to the GSL (GNU Scientific Library) processable format.
    """

    _is_upper_bound = None
    _maximal_exponent = 10.0

    def __init__(self, _is_upper_bound=False):
        # type: (bool) -> None
        """:param _is_upper_bound: Indicates whether an upper bound for the exponent shall be used."""
        self._is_upper_bound = _is_upper_bound
        return

    # TODO: Restructure this so the giant conditional goes away
    def convert_name_reference(self, _ast_variable):
        # type: (ASTVariable) -> str
        variable_name = GSLNamesConverter.convert_to_cpp_name(_ast_variable.getName())
        symbol = _ast_variable.getScope().resolveToSymbol(_ast_variable.getCompleteName(), SymbolKind.VARIABLE)

        if PredefinedUnits.isUnit(_ast_variable.getCompleteName()):
            return str(
                UnitConverter.getFactor(PredefinedUnits.getUnitIfExists(_ast_variable.getCompleteName()).getUnit()))
        if symbol.isInitValues():
            return GSLNamesConverter.name(symbol)
        elif symbol.isBuffer():
            return 'node.B_.' + GSLNamesConverter.buffer_value(symbol)
        elif variable_name == PredefinedVariables.E_CONSTANT:
            return 'numerics::e'
        elif symbol.isLocal() or symbol.isFunction():
            return variable_name
        elif symbol.hasVectorParameter():
            return 'node.get_' + variable_name + '()[i]'
        else:
            return 'node.get_' + variable_name + '()'

    # TODO: Restructure this so the giant conditional goes away
    def convert_function_call(self, _ast_function_call):
        # type: (ASTFunctionCall) -> str
        function_name = _ast_function_call.getName()
        if function_name == 'resolution':
            return 'nest::Time::get_resolution().get_ms()'
        if function_name == 'steps':
            return 'nest::Time(nest::Time::ms((double) %s)).get_steps()'
        if function_name == PredefinedFunctions.POW:
            return 'std::pow(%s)'
        if function_name == PredefinedFunctions.LOG:
            return 'std::log(%s)'
        if function_name == PredefinedFunctions.EXPM1:
            return 'numerics::expm1(%s)'
        if function_name == PredefinedFunctions.EXP:
            if self._is_upper_bound:
                return 'std::exp(std::min(%s,' + str(self._maximal_exponent) + '))'
            else:
                return 'std::exp(%s)'
        if function_name == PredefinedFunctions.MAX or function_name == PredefinedFunctions.BOUNDED_MAX:
            return 'std::max(%s)'
        if function_name == PredefinedFunctions.MIN or function_name == PredefinedFunctions.BOUNDED_MIN:
            return 'std::min(%s)'
        if function_name == PredefinedFunctions.EMIT_SPIKE:
            return 'set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n' \
                   'nest::SpikeEvent se;\n' \
                   'nest::kernel().event_delivery_manager.send(*this, se, lag)'
        raise UnsupportedOperationException('Cannot map the function: "' + function_name + '".')

    def convert_constant(self, _constant_name):
        # type: (str) -> str
        return _constant_name

    def convert_unary_op(self, _unary_operator):
        # type: (ASTUnaryOperator) -> str
        return str(_unary_operator) + '(%s)'

    # TODO: this clashes with convert methods for other operator types! it should delegate to them!
    def convert_binary_op(self, _binary_operator):
        # type: (Union[ASTArithmeticOperator,ASTBitOperator,ASTComparisonOperator,ASTLogicalOperator]) -> str
        if isinstance(_binary_operator, ASTArithmeticOperator) and _binary_operator.isPowOp():
            return 'pow(%s, %s)'
        else:
            return '%s' + str(_binary_operator) + '%s'

    def convert_logical_not(self):
        # type: () -> str
        return NESTReferenceConverter.convert_logical_not()

    def convert_logical_operator(self, _op):
        # type: (ASTLogicalOperator) -> str
        return NESTReferenceConverter.convert_logical_operator(_op)

    def convert_comparison_operator(self, _op):
        # type: (ASTComparisonOperator) -> str
        return NESTReferenceConverter.convert_comparison_operator(_op)

    def convert_bit_operator(self, _op):
        # type: (ASTBitOperator) -> str
        return NESTReferenceConverter.convert_bit_operator(_op)

    def convert_encapsulated(self):
        # type: () -> str
        return NESTReferenceConverter.convert_encapsulated()

    def convert_ternary_operator(self):
        # type: () -> str
        return NESTReferenceConverter.convert_ternary_operator()

    def convert_arithmetic_operator(self, _op):
        # type: (ASTArithmeticOperator) -> str
        return NESTReferenceConverter.convert_arithmetic_operator(_op)


class UnsupportedOperationException(Exception):
    pass
