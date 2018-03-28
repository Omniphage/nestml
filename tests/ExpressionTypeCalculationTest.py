#
# ExpressionTypeCalculationTest.py
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

from pynestml.codegeneration.LoggingShortcuts import LoggingShortcuts
from pynestml.codegeneration.UnitConverter import UnitConverter
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.Scope import CannotResolveSymbolError
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.modelprocessor.UnitTypeSymbol import UnitTypeSymbol
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import MessageCode

# minor setup steps required
SymbolTable.initializeSymbolTable(ASTSourcePosition(_startLine=0, _startColumn=0, _endLine=0, _endColumn=0))
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedVariables.registerPredefinedVariables()
PredefinedFunctions.registerPredefinedFunctions()


class expressionTestVisitor(NESTMLVisitor):
    def end_visit_assignment(self, _assignment=None):
        scope = _assignment.getScope()
        varName = _assignment.getVariable().getName()

        _expr = _assignment.getExpression()

        try:
            varSymbol = scope.resolve_variable_symbol(varName)
        except CannotResolveSymbolError:
            LoggingShortcuts.log_could_not_resolve(varName, _assignment.getVariable())

        _equals = varSymbol.getTypeSymbol().equals(_expr.type)

        message = 'line ' + str(_expr.getSourcePosition()) + ' : LHS = ' + \
                  varSymbol.getTypeSymbol().getSymbolName() + \
                  ' RHS = ' + _expr.type.getSymbolName() + \
                  ' Equal ? ' + str(_equals)

        if isinstance(_expr.type, UnitTypeSymbol):
            message += " Neuroscience Factor: " + \
                       str(UnitConverter().getFactor(_expr.type.astropy_unit))

        Logger.logMessage(_errorPosition=_assignment.getSourcePosition(), _code=MessageCode.TYPE_MISMATCH,
                          _message=message, _logLevel=LOGGING_LEVEL.INFO)

        if _equals is False:
            Logger.logMessage(_message="Type mismatch in test!",
                              _code=MessageCode.TYPE_MISMATCH,
                              _errorPosition=_assignment.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return


class ExpressionTypeCalculationTest(unittest.TestCase):
    """
    A simple test that prints all top-level expression types in a file.
    """

    # TODO: this test needs to be refactored.
    def test(self):
        Logger.initLogger(LOGGING_LEVEL.NO)
        model = ModelParser.parse_model_from_file(
            os.path.join(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                       'resources', 'ExpressionTypeTest.nestml'))))
        Logger.setCurrentNeuron(model.getNeuronList()[0])
        expressionTestVisitor().handle(model)
        Logger.setCurrentNeuron(None)
        self.assertEqual(len(Logger.getAllMessagesOfLevelAndOrNeuron(model.getNeuronList()[0], LOGGING_LEVEL.ERROR)), 2)


if __name__ == '__main__':
    unittest.main()
