#
# ExpressionsPrettyPrinterTest.py
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
from __future__ import division

import unittest

from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter, TypesPrinter
from pynestml.codegeneration.NestReferenceConverter import NESTReferenceConverter
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.StatementIndexingVisitor import StatementIndexingVisitor
from tests.resources.TestModels import TestModels

Logger.initLogger(LOGGING_LEVEL.ERROR)
SymbolTable.initializeSymbolTable(ASTSourcePosition())
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedVariables.registerPredefinedVariables()
PredefinedFunctions.registerPredefinedFunctions()
printer = ExpressionsPrettyPrinter()


class ExpressionsPrettyPrinterTest(unittest.TestCase):
    """
    Test class for everything Unit related.
    """

    test_model = ModelParser.parse_model_from_string(TestModels.MagnitudeConversion.simple_assignment)
    statements = StatementIndexingVisitor.visit_node(test_model)

    def setUp(self):
        Logger.getLog().clear()

    def test_expression_after_magnitude_conversion_in_direct_assignment(self):
        # type: () -> None
        stmt = self.statements["milliVolt = 10V"]
        printed_rhs_expression = printer.print_expression(stmt.getAssignment().getExpression())
        self.assertEqual('1000.0 * (10*V)', printed_rhs_expression)

    def test_expression_after_nested_magnitude_conversion_in_direct_assignment(self):
        # type: () -> None
        stmt = self.statements["milliVolt = 10V + 5mV + 20V + 1kV"]
        printed_rhs_expression = printer.print_expression(stmt.getAssignment().getExpression())
        self.assertEqual('1000.0 * (10*V + 0.001 * (5*mV) + 20*V + 1000.0 * (1*kV))', printed_rhs_expression)

    def test_expression_after_magnitude_conversion_in_compound_assignment(self):
        # type: () -> None
        stmt = self.statements["Volt += 1200mV"]
        printed_rhs_expression = printer.print_expression(stmt.getAssignment().getExpression())
        self.assertEqual('0.001 * (1200*mV)', printed_rhs_expression)

    def test_expression_after_magnitude_conversion_in_declaration(self):
        # type: () -> None
        stmt = self.statements["milliVolt mV = 10V"]
        printed_rhs_expression = printer.print_expression(stmt.getExpression())
        self.assertEqual('1000.0 * (10*V)', printed_rhs_expression)

    def test_expression_after_magnitude_conversion_in_standalone_function_call(self):
        # type: () -> None
        stmt = self.statements["take_mV(10V)"]
        printed_function_call = printer.print_function_call(stmt.getFunctionCall())
        self.assertEqual('take_mV(1000.0 * (10*V))', printed_function_call)

    def test_expression_after_magnitude_conversion_in_rhs_function_call(self):
        # type: () -> None
        stmt = self.statements["milliVolt = take_mV_return_mV(10V)"]
        printed_function_call = printer.print_expression(stmt.getAssignment().getExpression())
        self.assertEqual('take_mV_return_mV(1000.0 * (10*V))', printed_function_call)

    def test_return_stmt_after_magnitude_conversion_in_function_body(self):
        # type: () -> None
        stmt = self.statements["return milliVolt"]
        printed_return_stmt = printer.print_expression(stmt.getReturnStmt().getExpression())
        self.assertEqual('0.001 * (milliVolt)', printed_return_stmt)

    def test_print_numeric_literal(self):
        # type: () -> None
        expression = ModelParser.parse_expression('1')
        printed_rhs_expression = printer.print_expression(expression)
        self.assertEqual('1', printed_rhs_expression)

    def test_print_inf(self):
        # type: () -> None
        expression = ModelParser.parse_expression('inf')
        printed_rhs_expression = printer.print_expression(expression)
        self.assertEqual('inf', printed_rhs_expression)

    def test_print_string(self):
        # type: () -> None
        expression = ModelParser.parse_expression('"testString"')
        printed_rhs_expression = printer.print_expression(expression)
        self.assertEqual('"testString"', printed_rhs_expression)

    def test_print_boolean_true(self):
        # type: () -> None
        expression = ModelParser.parse_expression('True')
        printed_rhs_expression = printer.print_expression(expression)
        self.assertEqual('true', printed_rhs_expression)

    def test_print_boolean_false(self):
        # type: () -> None
        expression = ModelParser.parse_expression('False')
        printed_rhs_expression = printer.print_expression(expression)
        self.assertEqual('false', printed_rhs_expression)

    def test_print_unary_minus(self):
        # type: () -> None
        expression = ModelParser.parse_expression('-4')
        printed_rhs_expression = printer.print_expression(expression)
        self.assertEqual('-4', printed_rhs_expression)

    def test_print_encapsulated(self):
        # type: () -> None
        expression = ModelParser.parse_expression('(foo)')
        printed_rhs_expression = printer.print_expression(expression)
        self.assertEqual('(foo)', printed_rhs_expression)

    def test_print_logical_not(self):
        # type: () -> None
        expression = ModelParser.parse_expression('not bar')
        printed_rhs_expression = printer.print_expression(expression)
        self.assertEqual('not bar', printed_rhs_expression)

    def test_print_ternary_operator(self):
        # type: () -> None
        expression = ModelParser.parse_expression('foo?bar:foobar')
        printed_rhs_expression = printer.print_expression(expression)
        self.assertEqual('(foo)?(bar):(foobar)', printed_rhs_expression)

    def test_print_invalid_expression_return_value(self):
        # type: () -> None
        expression = ASTSimpleExpression.makeASTSimpleExpression()
        printed_rhs_expression = printer.print_expression(expression)
        self.assertEqual('', printed_rhs_expression)

    def test_print_invalid_expression_return_value(self):
        # type: () -> None
        expression = ASTSimpleExpression.makeASTSimpleExpression()
        printed_rhs_expression = printer.print_expression(expression)
        message = Logger.getLog().values()[0][5]
        self.assertEqual('Unsupported expression in expression pretty printer!', message)

    def test_init_parameter_reference_converter(self):
        # type: () -> None
        converter = NESTReferenceConverter()
        test_printer = ExpressionsPrettyPrinter(_reference_converter=converter)
        self.assertEqual(test_printer._reference_converter, converter)

    def test_init_parameter_types_printer(self):
        # type: () -> None
        types_printer = TypesPrinter()
        test_printer = ExpressionsPrettyPrinter(_types_printer=types_printer)
        self.assertEqual(test_printer._types_printer, types_printer)
