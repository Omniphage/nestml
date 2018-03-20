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
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.utils.Logger import LOGGING_LEVEL, Logger


class ExpressionsPrettyPrinterTest(unittest.TestCase):
    """
    Test class for everything Unit related.
    """

    # test_model = ModelParser.parse_model_from_string(TestModels.MagnitudeConversion.simple_assignment)
    # statements = StatementIndexingVisitor.visit_node(test_model)

    class_under_test = ExpressionsPrettyPrinter()

    # TODO: Rework this with mocks
    # noinspection PyPep8Naming
    def setUp(self):
        # type: () -> None
        Logger.getLog().clear()
        Logger.initLogger(LOGGING_LEVEL.ERROR)

    def test_print_implicit_conversion(self):
        # type: () -> None
        expression = ModelParser.parse_expression('270 nS')
        expression.setImplicitConversionFactor(0.001)
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('0.001 * (270*nS)', printed_rhs_expression)

    def test_print_numeric_literal_with_unit(self):
        # type: () -> None
        expression = ModelParser.parse_expression('7 mA')
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('7*mA', printed_rhs_expression)

    def test_print_compound_assignment(self):
        # type: () -> None
        expression = ModelParser.parse_expression('lhs + rhs')
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('lhs + rhs', printed_rhs_expression)

    def test_print_numeric_literal(self):
        # type: () -> None
        expression = ModelParser.parse_expression('1')
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('1', printed_rhs_expression)

    def test_print_inf(self):
        # type: () -> None
        expression = ModelParser.parse_expression('inf')
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('inf', printed_rhs_expression)

    def test_print_string(self):
        # type: () -> None
        expression = ModelParser.parse_expression('"testString"')
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('"testString"', printed_rhs_expression)

    def test_print_boolean_true(self):
        # type: () -> None
        expression = ModelParser.parse_expression('True')
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('true', printed_rhs_expression)

    def test_print_boolean_false(self):
        # type: () -> None
        expression = ModelParser.parse_expression('False')
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('false', printed_rhs_expression)

    def test_print_unary_minus(self):
        # type: () -> None
        expression = ModelParser.parse_expression('-4')
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('-4', printed_rhs_expression)

    def test_print_encapsulated(self):
        # type: () -> None
        expression = ModelParser.parse_expression('(foo)')
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('(foo)', printed_rhs_expression)

    def test_print_logical_not(self):
        # type: () -> None
        expression = ModelParser.parse_expression('not bar')
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('not bar', printed_rhs_expression)

    def test_print_ternary_operator(self):
        # type: () -> None
        expression = ModelParser.parse_expression('foo?bar:foobar')
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('(foo)?(bar):(foobar)', printed_rhs_expression)

    def test_print_function_without_parameters(self):
        # type: () -> None
        expression = ModelParser.parse_expression('foo()')
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('foo()', printed_rhs_expression)

    def test_print_function_with_two_parameters(self):
        # type: () -> None
        expression = ModelParser.parse_expression('foo(a, b)')
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('foo(a, b)', printed_rhs_expression)

    def test_print_invalid_expression_return_value(self):
        # type: () -> None
        expression = ASTSimpleExpression.makeASTSimpleExpression()
        printed_rhs_expression = self.class_under_test.print_expression(expression)
        self.assertEqual('', printed_rhs_expression)

    def test_print_invalid_expression_log_message(self):
        # type: () -> None
        expression = ASTSimpleExpression.makeASTSimpleExpression()
        self.class_under_test.print_expression(expression)
        (a, b, c, d, e, message) = Logger.getLog()[0]
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
