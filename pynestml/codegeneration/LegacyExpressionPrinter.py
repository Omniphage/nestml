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
from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.codegeneration.UnitConverter import UnitConverter
from pynestml.codegeneration.IdempotentReferenceConverter import IdempotentReferenceConverter


class LegacyExpressionPrinter(ExpressionsPrettyPrinter):
    """
    An adjusted version of the pretty printer which does not print units with literals.
    """
    __referenceConverter = None
    __typesPrinter = None

    def __init__(self, _referenceConverter=None):
        """
        Standard constructor.
        :param _referenceConverter: a single reference converter object.
        :type _referenceConverter: IReferenceConverter
        """
        from pynestml.codegeneration.ExpressionsPrettyPrinter import TypesPrinter
        super(LegacyExpressionPrinter, self).__init__(_referenceConverter)
        if _referenceConverter is not None:
            self.__referenceConverter = _referenceConverter
        else:
            self.__referenceConverter = IdempotentReferenceConverter()
        self.__typesPrinter = TypesPrinter()

    def doPrint(self, _expr=None):
        """
        Prints a single expression.
        :param _expr: a single expression.
        :type _expr: ASTExpression or ASTSimpleExpression.
        :return: string representation of the expression
        :rtype: str
        """
        if isinstance(_expr, ASTSimpleExpression):
            if _expr.isNumericLiteral():
                return self.__typesPrinter.pretty_print(_expr.getNumericLiteral())
            elif _expr.isInfLiteral():
                return self.__referenceConverter.convertConstant('inf')
            elif _expr.isString():
                return self.__typesPrinter.pretty_print(_expr.getString())
            elif _expr.isBooleanTrue():
                return self.__typesPrinter.pretty_print(True)
            elif _expr.isBooleanFalse():
                return self.__typesPrinter.pretty_print(False)
            elif _expr.isVariable():
                return self.__referenceConverter.convertNameReference(_expr.getVariable())
            elif _expr.isFunctionCall():
                return self.print_function_call(_expr.getFunctionCall())
        elif isinstance(_expr, ASTExpression):
            if _expr.isUnaryOperator():
                if _expr.getUnaryOperator().isUnaryPlus():
                    return '(' + self.__referenceConverter.convertUnaryOp('+') + \
                           self.print_expression(_expr.getExpression()) + ')'
                elif _expr.getUnaryOperator().isUnaryMinus():
                    return '(' + self.__referenceConverter.convertUnaryOp('-') + \
                           self.print_expression(_expr.getExpression()) + ')'
                elif _expr.getUnaryOperator().isUnaryTilde():
                    return '(' + self.__referenceConverter.convertUnaryOp('~') + \
                           self.print_expression(_expr.getExpression()) + ')'
            elif _expr.isEncapsulated():
                return '(' + self.print_expression(_expr.getExpression()) + ')'
            # logical not
            elif _expr.isLogicalNot():
                return self.__referenceConverter.convertUnaryOp('not') + ' ' + \
                       self.print_expression(_expr.getExpression())
            # compound expression with lhs + rhs
            elif _expr.isCompoundExpression():
                # arithmetic op, i.e. +,-,*,/
                if isinstance(_expr.getBinaryOperator(), ASTArithmeticOperator) and \
                        (_expr.getBinaryOperator().isTimesOp() or _expr.getBinaryOperator().isDivOp() or
                             _expr.getBinaryOperator().isMinusOp() or _expr.getBinaryOperator().isPlusOp() or
                             _expr.getBinaryOperator().isModuloOp()):
                    return self.print_expression(_expr.getLhs()) + ' ' + \
                           self.printArithmeticOperator(_expr.getBinaryOperator()) + ' ' + \
                           self.print_expression(_expr.getRhs())
                # pow op
                elif isinstance(_expr.getBinaryOperator(),
                                ASTArithmeticOperator) and _expr.getBinaryOperator().isPowOp():
                    lhs = self.print_expression(_expr.getLhs())
                    pow = self.__referenceConverter.convertBinaryOp('**')
                    rhs = self.print_expression(_expr.getRhs())
                    return pow % (lhs, rhs)
                # bit operator
                elif isinstance(_expr.getBinaryOperator(), ASTBitOperator):
                    lhs = self.print_expression(_expr.getLhs())
                    bit = self.printBitOperator(_expr.getBinaryOperator())
                    rhs = self.print_expression(_expr.getRhs())
                    return lhs + ' ' + bit + ' ' + rhs
                # comparison operator
                elif isinstance(_expr.getBinaryOperator(), ASTComparisonOperator):
                    lhs = self.print_expression(_expr.getLhs())
                    comp = self.printComparisonOperator(_expr.getBinaryOperator())
                    rhs = self.print_expression(_expr.getRhs())
                    return lhs + ' ' + comp + ' ' + rhs
                elif isinstance(_expr.getBinaryOperator(), ASTLogicalOperator):
                    lhs = self.print_expression(_expr.getLhs())
                    op = self.printLogicalOperator(_expr.getBinaryOperator())
                    rhs = self.print_expression(_expr.getRhs())
                    return op % (lhs, rhs)

            elif _expr.isTernaryOperator():
                condition = self.print_expression(_expr.getCondition())
                ifTrue = self.print_expression(_expr.getIfTrue())
                ifNot = self.print_expression(_expr.getIfNot())
                return '(' + condition + ')?(' + ifTrue + '):(' + ifNot + ')'
        else:
            Logger.logMessage('Unsupported expression in expression pretty printer!', LOGGING_LEVEL.ERROR)
            return ''
