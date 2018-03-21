#
# IdempotentReferenceConverterTest.py
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

from mock import MagicMock, Mock, patch

from pynestml.codegeneration.IdempotentReferenceConverter import IdempotentReferenceConverter
from pynestml.modelprocessor.ASTFunction import ASTFunction


# noinspection PyMissingTypeHints,PyTypeChecker
class IdempotentReferenceConverterTest(unittest.TestCase):
    class_under_test = None

    # noinspection PyPep8Naming
    def setUp(self):
        self.class_under_test = IdempotentReferenceConverter()

    def test_convert_name_reference(self):
        variable = Mock()
        result = self.class_under_test.convert_name_reference(variable)
        self.assertEqual(variable.getCompleteName(), result)

    @patch('pynestml.codegeneration.IdempotentReferenceConverter.ASTUtils')
    def test_convert_function_call_with_parameters(self, _mock_utils):
        func = MagicMock(ASTFunction)
        func.getName.return_value = 'foo'
        _mock_utils.needsArguments.return_value = True
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual('foo(%s)', result)

    @patch('pynestml.codegeneration.IdempotentReferenceConverter.ASTUtils')
    def test_convert_function_call_no_parameters(self, _mock_utils):
        func = MagicMock(ASTFunction)
        func.getName.return_value = 'foo'
        _mock_utils.needsArguments.return_value = False
        result = self.class_under_test.convert_function_call(func)
        self.assertEqual('foo()', result)

    def test_convert_constant(self):
        constant = 'foo'
        result = self.class_under_test.convert_constant(constant)
        self.assertEqual('foo', result)

    def test_convert_unary_op(self):
        unary_op = Mock()
        result = self.class_under_test.convert_unary_op(unary_op)
        self.assertEqual(str(unary_op) + '%s', result)

    def test_convert_binary_op_with_arithmetic_non_pow(self):
        binary_op = Mock()
        result = self.class_under_test.convert_binary_op(binary_op)
        self.assertEqual('%s' + str(binary_op) + '%s', result)

    def test_convert_logical_not(self):
        result = self.class_under_test.convert_logical_not()
        self.assertEqual('not %s', result)

    def test_convert_logical_op(self):
        logical_op = Mock()
        result = self.class_under_test.convert_logical_operator(logical_op)
        self.assertEqual(str(logical_op), result)

    def test_convert_comparison_op(self):
        comparison_op = Mock()
        result = self.class_under_test.convert_comparison_operator(comparison_op)
        self.assertEqual(str(comparison_op), result)

    def test_convert_bit_op(self):
        bit_op = Mock()
        result = self.class_under_test.convert_bit_operator(bit_op)
        self.assertEqual(str(bit_op), result)

    def test_convert_encapsulated(self):
        result = self.class_under_test.convert_encapsulated()
        self.assertEqual('(%s)', result)

    def test_convert_ternary_op(self):
        result = self.class_under_test.convert_ternary_operator()
        self.assertEqual('(%s)?(%s):(%s)', result)

    def test_convert_arithmetic_op(self):
        arith_op = Mock()
        result = self.class_under_test.convert_arithmetic_operator(arith_op)
        self.assertEqual(str(arith_op), result)
