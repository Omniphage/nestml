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

import os

from coverage import Coverage
coverage = None

if os.environ['run_coverage'] == 'True':
    # type: () -> None
    coverage = Coverage()
    coverage.set_option('run:include', ['../pynestml/codegeneration/ExpressionsPrettyPrinter.py'])
    coverage.set_option('run:data_file', 'coverage_reports/ExpressionsPrettyPrinter.rep')
    coverage.start()

from nose.tools import nottest

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
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.StatementIndexingVisitor import StatementIndexingVisitor
from tests.PyNestmlCoveredTest import PyNestmlCoveredTest
from tests.resources.TestModels import TestModels

SymbolTable.initializeSymbolTable(ASTSourcePosition())
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedVariables.registerPredefinedVariables()
PredefinedFunctions.registerPredefinedFunctions()
printer = NestPrinter(ExpressionsPrettyPrinter(), NESTReferenceConverter())


class ExpressionsPrettyPrinterTest(PyNestmlCoveredTest):
    """
    Test class for everything Unit related.
    """

    test_model = ModelParser.parse_model_from_string(TestModels.MagnitudeConversion.simple_assignment)
    statements = StatementIndexingVisitor.visit_node(test_model)

    @staticmethod
    def set_logging_level():
        # type: () -> None
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)

    @staticmethod
    @nottest
    def set_module_under_test():
        # type: () -> None
        ExpressionsPrettyPrinterTest.module_under_test = '../pynestml/codegeneration/ExpressionsPrettyPrinter.py'

    def test_expression_after_magnitude_conversion_in_direct_assignment(self):
        # type: () -> None
        stmt = self.statements["milliVolt = 10V"]
        printed_rhs_expression = printer.printExpression(stmt.getAssignment().getExpression())
        self.assertEqual('1000.0 * (10*V)', printed_rhs_expression)

    def test_expression_after_nested_magnitude_conversion_in_direct_assignment(self):
        # type: () -> None
        stmt = self.statements["milliVolt = 10V + 5mV + 20V + 1kV"]
        printed_rhs_expression = printer.printExpression(stmt.getAssignment().getExpression())
        self.assertEqual('1000.0 * (10*V + 0.001 * (5*mV) + 20*V + 1000.0 * (1*kV))', printed_rhs_expression)

    def test_expression_after_magnitude_conversion_in_compound_assignment(self):
        # type: () -> None
        stmt = self.statements["Volt += 1200mV"]
        printed_rhs_expression = printer.printExpression(stmt.getAssignment().getExpression())
        self.assertEqual('0.001 * (1200*mV)', printed_rhs_expression)

    def test_expression_after_magnitude_conversion_in_declaration(self):
        # type: () -> None
        stmt = self.statements["milliVolt mV = 10V"]
        printed_rhs_expression = printer.printExpression(stmt.getExpression())
        self.assertEqual('1000.0 * (10*V)', printed_rhs_expression)

    def test_expression_after_magnitude_conversion_in_standalone_function_call(self):
        # type: () -> None
        stmt = self.statements["take_mV(10V)"]
        printed_function_call = printer.print_function_call(stmt.getFunctionCall())
        self.assertEqual('take_mV(1000.0 * (10*V))', printed_function_call)

    def test_expression_after_magnitude_conversion_in_rhs_function_call(self):
        # type: () -> None
        stmt = self.statements["milliVolt = take_mV_return_mV(10V)"]
        printed_function_call = printer.printExpression(stmt.getAssignment().getExpression())
        self.assertEqual('take_mV_return_mV(1000.0 * (10*V))', printed_function_call)

    def test_return_stmt_after_magnitude_conversion_in_function_body(self):
        # type: () -> None
        stmt = self.statements["return milliVolt"]
        printed_return_stmt = printer.printExpression(stmt.getReturnStmt().getExpression())
        self.assertEqual('0.001 * (milliVolt)', printed_return_stmt)


coverage.stop()
coverage.save()
