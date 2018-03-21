#
# LegacyExpressionPrinterTest.py
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
import unittest

from mock import Mock, patch

from pynestml.codegeneration.ExpressionsPrettyPrinter import TypesPrinter
from pynestml.codegeneration.LegacyExpressionPrinter import LegacyExpressionPrinter
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression


# noinspection PyTypeChecker,PyMissingTypeHints
class LegacyExpressionPrinterTest(unittest.TestCase):
    class_under_test = None
    mock_types_printer = None
    mock_simple_expression = None

    # noinspection PyPep8Naming
    def setUp(self):
        self.class_under_test = LegacyExpressionPrinter()
        self.mock_types_printer = Mock(TypesPrinter)
        self.mock_simple_expression = Mock(ASTSimpleExpression)

    def test_do_print_simple_expression_with_literal_and_unit(self):
        self.class_under_test._types_printer = self.mock_types_printer
        result = self.class_under_test._do_print(self.mock_simple_expression)
        self.assertEqual(self.mock_types_printer.pretty_print(), result)

    def test_do_print_simple_expression_without_literal(self):
        self.mock_simple_expression.isNumericLiteral.return_value = False
        self.class_under_test._types_printer = self.mock_types_printer
        result = self.class_under_test._do_print(self.mock_simple_expression)
        self.assertEqual(self.mock_types_printer.pretty_print(), result)

    def test_do_print_simple_expression_without_unit(self):
        self.mock_simple_expression.hasUnit.return_value = False
        self.class_under_test._types_printer = self.mock_types_printer
        result = self.class_under_test._do_print(self.mock_simple_expression)
        self.assertEqual(self.mock_types_printer.pretty_print(), result)

    @patch('pynestml.codegeneration.LegacyExpressionPrinter.super')
    def test_do_print_simple_expression_without_unit_and_literal(self, _mock_super):
        self.mock_simple_expression.isNumericLiteral.return_value = False
        self.mock_simple_expression.hasUnit.return_value = False
        self.class_under_test._do_print(self.mock_simple_expression)
        _mock_super.assert_called()

    @patch('pynestml.codegeneration.LegacyExpressionPrinter.super')
    def test_do_print_expression(self, _mock_super):
        expression = Mock(ASTExpression)
        self.class_under_test._types_printer = self.mock_types_printer
        self.class_under_test._do_print(expression)
        _mock_super.assert_called()