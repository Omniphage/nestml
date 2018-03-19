#
# unit_system_test.py
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
import os
import unittest

from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter
from pynestml.codegeneration.NestPrinter import NestPrinter
from pynestml.codegeneration.NestReferenceConverter import NESTReferenceConverter
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.utils.Logger import Logger, LOGGING_LEVEL

SymbolTable.initializeSymbolTable(ASTSourcePosition())
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedVariables.registerPredefinedVariables()
PredefinedFunctions.registerPredefinedFunctions()
printer = NestPrinter(ExpressionsPrettyPrinter(), NESTReferenceConverter())


def get_first_statement_in_update_block(model):
    return model.getNeuronList()[0].getUpdateBlocks().getBlock().getStmts()[0]


def get_first_declaration_in_state_block(model):
    return model.getNeuronList()[0].getStateBlocks().getDeclarations()[0]


def get_first_declared_function(model):
    return model.getNeuronList()[0].getFunctions()[0]


def print_rhs_of_first_assignment_in_update_block(model):
    assignment = get_first_statement_in_update_block(model).getAssignment()
    expression = assignment.getExpression()
    return printer.printExpression(expression)


def print_first_function_call_in_update_block(model):
    functon_call = get_first_statement_in_update_block(model).getFunctionCall()
    return printer.printMethodCall(functon_call)


def print_rhs_of_first_declaration_in_state_block(model):
    declaration = get_first_declaration_in_state_block(model)
    expression = declaration.getExpression()
    return printer.printExpression(expression)


def print_first_return_statement_in_first_declared_function(model):
    function = get_first_declared_function(model)
    return_expression = function.getBlock().getStmts()[0].getReturnStmt().getExpression()
    return printer.printExpression(return_expression)



class UnitSystemTest(unittest.TestCase):
    """
    Test class for everything Unit related.
    """

    def setUp(self):
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)

    def test_expression_after_magnitude_conversion_in_direct_assignment(self):
        model = ModelParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')),
                         'DirectAssignmentWithDifferentButCompatibleUnits.nestml'))
        printed_rhs_expression = print_rhs_of_first_assignment_in_update_block(model)
        self.assertEqual(printed_rhs_expression, '1000.0 * (10*V)')

    def test_expression_after_nested_magnitude_conversion_in_direct_assignment(self):
        model = ModelParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')),
                         'DirectAssignmentWithDifferentButCompatibleNestedUnits.nestml'))
        printed_rhs_expression = print_rhs_of_first_assignment_in_update_block(model)
        self.assertEqual(printed_rhs_expression, '1000.0 * (10*V + 0.001 * (5*mV) + 20*V + 1000.0 * (1*kV))')

    def test_expression_after_magnitude_conversion_in_compound_assignment(self):
        model = ModelParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')),
                         'CompoundAssignmentWithDifferentButCompatibleUnits.nestml'))
        printed_rhs_expression = print_rhs_of_first_assignment_in_update_block(model)
        self.assertEqual(printed_rhs_expression, '0.001 * (1200*mV)')

    def test_expression_after_magnitude_conversion_in_declaration(self):
        model = ModelParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')),
                         'DeclarationWithDifferentButCompatibleUnits.nestml'))
        printed_rhs_expression = print_rhs_of_first_declaration_in_state_block(model)
        self.assertEqual(printed_rhs_expression, '1000.0 * (10*V)')

    def test_expression_after_magnitude_conversion_in_standalone_function_call(self):
        model = ModelParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')),
                         'FunctionCallWithDifferentButCompatibleUnits.nestml'))
        printed_function_call = print_first_function_call_in_update_block(model)
        self.assertEqual(printed_function_call, 'foo(1000.0 * (10*V))')

    def test_expression_after_magnitude_conversion_in_rhs_function_call(self):
        model = ModelParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')),
                         'RhsFunctionCallWithDifferentButCompatibleUnits.nestml'))
        printed_function_call = print_rhs_of_first_assignment_in_update_block(model)
        self.assertEqual(printed_function_call, 'foo(1000.0 * (10*V))')

    def test_return_stmt_after_magnitude_conversion_in_function_body(self):
        model = ModelParser.parseModel(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__), 'resources')),
                         'FunctionBodyReturnStatementWithDifferentButCompatibleUnits.nestml'))
        printed_return_stmt = print_first_return_statement_in_first_declared_function(model)
        self.assertEqual(printed_return_stmt, '0.001 * (bar)')
