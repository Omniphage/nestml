#
# NestAssignmentsHelperTest.py
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

from pynestml.codegeneration.NestAssignmentsHelper import NestAssignmentsHelper
from pynestml.modelprocessor.ASTAssignment import ASTAssignment
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.utils.Logger import Logger, LOGGING_LEVEL


# noinspection PyTypeChecker,PyMissingTypeHints
class NestAssignmentsHelperTest(unittest.TestCase):
    class_under_test = None
    mock_assignment = None

    # noinspection PyPep8Naming
    def setUp(self):
        self.class_under_test = NestAssignmentsHelper()
        self.mock_assignment = Mock(ASTAssignment)
        Logger.initLogger(LOGGING_LEVEL.ERROR)

    def test_lhs_variable_with_resovable_symbol(self):
        scope = self.mock_assignment.getScope.return_value.resolveToSymbol.return_value
        result = self.class_under_test.lhs_variable(self.mock_assignment)
        self.assertEqual(scope, result)

    def test_lhs_variable_with_unresovable_symbol(self):
        self.mock_assignment.getScope.return_value.resolveToSymbol.return_value = None
        self.mock_assignment.getVariable.return_value.getCompleteName.return_value = 'somevar'
        self.class_under_test.lhs_variable(self.mock_assignment)
        (a, b, c, d, e, message) = Logger.getLog()[0]
        self.assertEqual('Could not resolve symbol \'somevar\'!', message)

    def test_print_assignments_operation_with_compound_sum(self):
        result = self.class_under_test.print_assignments_operation(self.mock_assignment)
        self.assertEqual('+=', result)

    def test_print_assignments_operation_with_compound_mius(self):
        self.mock_assignment.isCompoundSum.return_value = False
        result = self.class_under_test.print_assignments_operation(self.mock_assignment)
        self.assertEqual('-=', result)

    def test_print_assignments_operation_with_compound_product(self):
        self.mock_assignment.isCompoundSum.return_value = False
        self.mock_assignment.isCompoundMinus.return_value = False
        result = self.class_under_test.print_assignments_operation(self.mock_assignment)
        self.assertEqual('*=', result)

    def test_print_assignments_operation_with_compound_quotient(self):
        self.mock_assignment.isCompoundSum.return_value = False
        self.mock_assignment.isCompoundMinus.return_value = False
        self.mock_assignment.isCompoundProduct.return_value = False
        result = self.class_under_test.print_assignments_operation(self.mock_assignment)
        self.assertEqual('/=', result)

    def test_print_assignments_operation_with_simple_assignment(self):
        self.mock_assignment.isCompoundSum.return_value = False
        self.mock_assignment.isCompoundMinus.return_value = False
        self.mock_assignment.isCompoundProduct.return_value = False
        self.mock_assignment.isCompoundQuotient.return_value = False
        result = self.class_under_test.print_assignments_operation(self.mock_assignment)
        self.assertEqual('=', result)

    @patch('tests.codegeneration.NestAssignmentsHelperTest.NestAssignmentsHelper.variable_has_vector_parameter')
    def test_is_vectorized_assignment_with_vector_parameter(self, _mock_helper_function):
        self.mock_assignment.getExpression.return_value.getVariables.return_value = [Mock()]
        _mock_helper_function.return_value = True
        result = self.class_under_test.is_vectorized_assignment(self.mock_assignment)
        self.assertEqual(True, result)

    @patch('tests.codegeneration.NestAssignmentsHelperTest.NestAssignmentsHelper.variable_has_vector_parameter')
    def test_is_vectorized_assignment_without_vector_parameter(self, _mock_helper_function):
        self.mock_assignment.getExpression.return_value.getVariables.return_value = [Mock()]
        self.mock_assignment.getVariable.return_value.getCompleteName.return_value = 'somevar'
        _mock_helper_function.return_value = False
        self.class_under_test.is_vectorized_assignment(self.mock_assignment)
        (a, b, c, d, e, message) = Logger.getLog()[0]
        self.assertEqual('Could not resolve symbol \'somevar\'!', message)

    def test_variable_has_vector_parameter_without_symbol(self):
        var = Mock(ASTVariable)
        var.getScope.return_value.resolveToSymbol.return_value = None
        result = self.class_under_test.variable_has_vector_parameter(var)
        self.assertEqual(False, result)

    def test_variable_has_vector_parameter_with_symbol_no_vector_parameter(self):
        var = Mock(ASTVariable)
        var.getScope.return_value.resolveToSymbol.return_value.hasVectorParameter.return_value = False
        result = self.class_under_test.variable_has_vector_parameter(var)
        self.assertEqual(False, result)

    def test_variable_has_vector_parameter_with_symbol_and_vector_parameter(self):
        var = Mock(ASTVariable)
        result = self.class_under_test.variable_has_vector_parameter(var)
        self.assertEqual(True, result)

    def test_print_size_parameter_expression_var_has_symbol_is_vector(self):
        var = Mock(ASTVariable)
        sym = var.getScope.return_value.resolveToSymbol.return_value
        self.mock_assignment.getExpression.return_value.getVariables.return_value = [var]
        result = self.class_under_test.print_size_parameter(self.mock_assignment)
        self.assertEqual(sym.getVectorParameter(), result)

    def test_print_size_parameter_expression_var_has_no_symbol(self):
        expr_var = Mock(ASTVariable)
        expr_var.getScope.return_value.resolveToSymbol.return_value = None
        self.mock_assignment.getExpression.return_value.getVariables.return_value = [expr_var]
        result = self.class_under_test.print_size_parameter(self.mock_assignment)
        self.mock_assignment.getScope.return_value.resolveToSymbol.assert_called_with(
            self.mock_assignment.getVariable().getCompleteName(), SymbolKind.VARIABLE)

    def test_print_size_parameter_expression_var_has_symbol_is_no_vector(self):
        expr_var = Mock(ASTVariable)
        expr_var.getScope.return_value.resolveToSymbol.return_value.hasVectorParameter.return_value = False
        self.mock_assignment.getExpression.return_value.getVariables.return_value = [expr_var]
        result = self.class_under_test.print_size_parameter(self.mock_assignment)
        self.mock_assignment.getScope.return_value.resolveToSymbol.assert_called_with(
            self.mock_assignment.getVariable().getCompleteName(), SymbolKind.VARIABLE)
