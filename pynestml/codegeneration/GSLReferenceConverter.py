#
# GSLReferenceConverter.py
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
from pynestml.codegeneration.GSLNamesConverter import GSLNamesConverter
from pynestml.codegeneration.IReferenceConverter import IReferenceConverter
from pynestml.codegeneration.NestNamesConverter import NestNamesConverter
from pynestml.codegeneration.NestReferenceConverter import NESTReferenceConverter
from pynestml.codegeneration.UnitConverter import UnitConverter
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
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

    __isUpperBound = None
    __maximalExponent = 10.0

    def __init__(self, _isUpperBound=False):
        # type: (bool) -> None
        """:param _isUpperBound: Indicates whether an upper bound for the exponent shall be used."""
        self.__isUpperBound = _isUpperBound
        return

    def convert_name_reference(self, _astVariable):
        # type: (ASTVariable) -> str
        variableName = NestNamesConverter.convertToCPPName(_astVariable.getName())
        symbol = _astVariable.getScope().resolveToSymbol(_astVariable.getCompleteName(), SymbolKind.VARIABLE)

        if PredefinedUnits.isUnit(_astVariable.getCompleteName()):
            return str(
                UnitConverter.getFactor(PredefinedUnits.getUnitIfExists(_astVariable.getCompleteName()).getUnit()))
        if symbol.isInitValues():
            return GSLNamesConverter.name(symbol)
        elif symbol.isBuffer():
            return 'node.B_.' + NestNamesConverter.bufferValue(symbol)
        elif variableName == PredefinedVariables.E_CONSTANT:
            return 'numerics::e'
        elif symbol.isLocal() or symbol.isFunction():
            return variableName
        elif symbol.hasVectorParameter():
            return 'node.get_' + variableName + '()[i]'
        else:
            return 'node.get_' + variableName + '()'

    def convert_function_call(self, _astFunctionCall):
        # type: (ASTFunctionCall) -> str
        functionName = _astFunctionCall.getName()
        if functionName == 'resolution':
            return 'nest::Time::get_resolution().get_ms()'
        if functionName == 'steps':
            return 'nest::Time(nest::Time::ms((double) %s)).get_steps()'
        if functionName == PredefinedFunctions.POW:
            return 'std::pow(%s)'
        if functionName == PredefinedFunctions.LOG:
            return 'std::log(%s)'
        if functionName == PredefinedFunctions.EXPM1:
            return 'numerics::expm1(%s)'
        if functionName == PredefinedFunctions.EXP:
            if self.__isUpperBound:
                return 'std::exp(std::min(%s,' + str(self.__maximalExponent) + '))'
            else:
                return 'std::exp(%s)'
        if functionName == PredefinedFunctions.MAX or functionName == PredefinedFunctions.BOUNDED_MAX:
            return 'std::max(%s)'
        if functionName == PredefinedFunctions.MIN or functionName == PredefinedFunctions.BOUNDED_MIN:
            return 'std::min(%s)'
        if functionName == PredefinedFunctions.EMIT_SPIKE:
            return 'set_spiketime(nest::Time::step(origin.get_steps()+lag+1));\n' \
                   'nest::SpikeEvent se;\n' \
                   'nest::kernel().event_delivery_manager.send(*this, se, lag)'
        raise UnsupportedOperationException('Cannot map the function: "' + functionName + '".')

    def convert_constant(self, _constantName):
        # type: (str) -> str
        return _constantName

    def convert_unary_op(self, _unaryOperator):
        # type: (ASTUnaryOperator) -> str
        return str(_unaryOperator) + '(%s)'

    def convert_binary_op(self, _binaryOperator):
        from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
        from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
        from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
        from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
        assert (_binaryOperator is not None and (isinstance(_binaryOperator, ASTArithmeticOperator) or
                                                 isinstance(_binaryOperator, ASTBitOperator) or
                                                 isinstance(_binaryOperator, ASTComparisonOperator) or
                                                 isinstance(_binaryOperator, ASTLogicalOperator))), \
            '(PyNestML.CodeGeneration.GSLReferenceConverter) No or wrong type of binary operator provided (%s)!' \
            % type(_binaryOperator)
        if isinstance(_binaryOperator, ASTArithmeticOperator) and _binaryOperator.isPowOp():
            return 'pow(%s, %s)'
        else:
            return '%s' + str(_binaryOperator) + '%s'

    def convert_logical_not(self):
        return NESTReferenceConverter.convert_logical_not()

    def convert_logical_operator(self, _op):
        return NESTReferenceConverter.convert_logical_operator(_op)

    def convert_comparison_operator(self, _op):
        return NESTReferenceConverter.convert_comparison_operator(_op)

    def convert_bit_operator(self, _op):
        return NESTReferenceConverter.convert_bit_operator(_op)

    def convert_encapsulated(self):
        return NESTReferenceConverter.convert_encapsulated()

    def convert_ternary_operator(self):
        return NESTReferenceConverter.convert_ternary_operator()

    def convert_arithmetic_operator(self, _op):
        return NESTReferenceConverter.convert_arithmetic_operator(_op)


class UnsupportedOperationException(Exception):
    pass
