#
# ExpressionsPrettyPrinter.py
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
from pynestml.codegeneration.IdempotentReferenceConverter import IdempotentReferenceConverter
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.utils.ASTUtils import ASTUtils
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages


class ExpressionsPrettyPrinter(object):
    """
    Converts expressions to the executable platform dependent code. By using different
    referenceConverters for the handling of variables, names, and functions can be adapted. For this,
    implement own IReferenceConverter specialisation.
    This class is used to transform only parts of the procedural language and not nestml in whole.
    """
    _reference_converter = None
    _types_printer = None

    def __init__(self, _reference_converter=None, _types_printer=None):
        # type: (IReferenceConverter, TypesPrinter) -> None
        if _reference_converter is not None:
            self._reference_converter = _reference_converter
        else:
            self._reference_converter = IdempotentReferenceConverter()
        if _types_printer is not None:
            self._types_printer = _types_printer
        else:
            self._types_printer = TypesPrinter()

    def print_expression(self, _expr):
        # type: (Union[ASTExpression,ASTSimpleExpression]) -> str
        if _expr.getImplicitConversionFactor() is not None:
            return str(_expr.getImplicitConversionFactor()) + ' * (' + self._do_print(_expr) + ')'
        else:
            return self._do_print(_expr)

    def _do_print(self, _expr):
        # type: (Union[ASTExpression,ASTSimpleExpression]) -> str
        if isinstance(_expr, ASTSimpleExpression):
            if _expr.hasUnit():
                return self._types_printer.pretty_print(_expr.getNumericLiteral()) + '*' + \
                       self._reference_converter.convert_name_reference(_expr.getVariable())
            elif _expr.isNumericLiteral():
                return self._types_printer.pretty_print(_expr.getNumericLiteral())
            elif _expr.isInfLiteral():
                return self._reference_converter.convert_constant('inf')
            elif _expr.isString():
                return self._types_printer.pretty_print(_expr.getString())
            elif _expr.isBooleanTrue():
                return self._types_printer.pretty_print(True)
            elif _expr.isBooleanFalse():
                return self._types_printer.pretty_print(False)
            elif _expr.isVariable():
                return self._reference_converter.convert_name_reference(_expr.getVariable())
            elif _expr.isFunctionCall():
                return self.print_function_call(_expr.getFunctionCall())
        elif isinstance(_expr, ASTExpression):
            # a unary operator
            if _expr.isUnaryOperator():
                op = self._reference_converter.convert_unary_op(_expr.getUnaryOperator())
                rhs = self.print_expression(_expr.getExpression())
                return op % rhs
            # encapsulated in brackets
            elif _expr.isEncapsulated():
                return self._reference_converter.convert_encapsulated() % self.print_expression(_expr.getExpression())
            # logical not
            elif _expr.isLogicalNot():
                op = self._reference_converter.convert_logical_not()
                rhs = self.print_expression(_expr.getExpression())
                return op % rhs
            # compound expression with lhs + rhs
            elif _expr.isCompoundExpression():
                lhs = self.print_expression(_expr.getLhs())
                op = self._reference_converter.convert_binary_op(_expr.getBinaryOperator())
                rhs = self.print_expression(_expr.getRhs())
                return op % (lhs, rhs)
            elif _expr.isTernaryOperator():
                condition = self.print_expression(_expr.getCondition())
                if_true = self.print_expression(_expr.getIfTrue())
                if_not = self.print_expression(_expr.getIfNot())
                return self._reference_converter.convert_ternary_operator() % (condition, if_true, if_not)
        code, message = Messages.get_unsupported_expression_in_pretty_printer()
        Logger.logMessage(_code=code, _message=message, _errorPosition=_expr.getSourcePosition(),
                          _logLevel=LOGGING_LEVEL.ERROR)
        return ''

    def print_function_call(self, _function_call):
        # type: (ASTFunctionCall) -> str
        function_name = self._reference_converter.convert_function_call(_function_call)
        if ASTUtils.needsArguments(_function_call):
            return function_name % self.print_function_call_arguments(_function_call)
        else:
            return function_name

    def print_function_call_arguments(self, _function_call):
        # type: (ASTFunctionCall) -> str
        ret = ''
        for arg in _function_call.getArgs():
            ret += self.print_expression(arg)
            if _function_call.getArgs().index(arg) < len(_function_call.getArgs()) - 1:
                ret += ', '
        return ret


class TypesPrinter(object):
    @staticmethod
    def pretty_print(_element):
        # type: (Union[bool,int,str]) -> str
        if isinstance(_element, bool) and _element:
            return 'true'
        elif isinstance(_element, bool) and not _element:
            return 'false'
        elif isinstance(_element, int) or isinstance(_element, float):
            return str(_element)
        elif isinstance(_element, str):
            return _element
