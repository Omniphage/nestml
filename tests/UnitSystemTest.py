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
from __future__ import division

import os
import unittest

from coverage import Coverage
from typing import Dict, Union

from pynestml.codegeneration.ExpressionsPrettyPrinter import ExpressionsPrettyPrinter
from pynestml.codegeneration.NestPrinter import NestPrinter
from pynestml.codegeneration.NestReferenceConverter import NESTReferenceConverter
from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
from pynestml.modelprocessor.ASTDeclaration import ASTDeclaration
from pynestml.modelprocessor.ASTNode import ASTNode
from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from tests.resources.TestModels import TestModels

SymbolTable.initializeSymbolTable(ASTSourcePosition())
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedVariables.registerPredefinedVariables()
PredefinedFunctions.registerPredefinedFunctions()
printer = NestPrinter(ExpressionsPrettyPrinter(), NESTReferenceConverter())


class StatementIndexingVisitor(NESTMLVisitor):

    def __init__(self):
        # type: () -> None
        super(StatementIndexingVisitor, self).__init__()
        self.result = {}

    def visit_compound_stmt(self, _stmt):
        # type: (ASTCompoundStmt) -> None
        self.result[str(_stmt)] = _stmt

    def visit_small_stmt(self, _stmt):
        # type: (ASTSmallStmt) -> None
        self.result[str(_stmt)] = _stmt

    def visit_declaration(self, _declaration):
        # type: (ASTDeclaration) -> None
        self.result[str(_declaration)] = _declaration

    @staticmethod
    def visit_node(_node):
        # type: (ASTNode) -> Dict[str,Union[ASTCompoundStmt,ASTSmallStmt,ASTDeclaration]]
        instance = StatementIndexingVisitor()
        _node.accept(instance)
        return instance.result


class UnitSystemTest(unittest.TestCase):
    """
    Test class for everything Unit related.
    """
    coverage = None

    @classmethod
    def setUpClass(cls):
        # type: () -> None
        Logger.setLoggingLevel(LOGGING_LEVEL.NO)
        cls.test_model = ModelParser.parse_model_from_string(TestModels.MagnitudeConversion.simple_assignment)
        cls.statements = StatementIndexingVisitor.visit_node(cls.test_model)
        if os.environ['run_coverage'] == 'True':
            cls.coverage = Coverage()
            cls.coverage.start()
            cls.coverage.set_option('run:include', ["*/ExpressionsPrettyPrinter.py"])

    @classmethod
    def tearDownClass(cls):
        # type: () -> None
        if os.environ['run_coverage'] == 'True':
            cls.coverage.stop()
            name, executable, excluded, missing, formatted_missing = cls.coverage.analysis2(
                "../pynestml/codegeneration/ExpressionsPrettyPrinter.py")
            total = len(executable) - len(excluded)
            print 'total: ' + str(total)
            executed = total - len(missing)
            print 'executed: ' + str(executed)
            percentage = executed / total
            pretty_percentage = round(percentage * 100, 2)
            threshold = 95.00
            assert pretty_percentage > threshold, "Test coverage is %s. Target is %s" % (pretty_percentage, threshold)

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
