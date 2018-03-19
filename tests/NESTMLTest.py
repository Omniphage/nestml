#
# NESTMLTest.py
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

from __future__ import print_function

import unittest
import os
from unittest import SkipTest

from pynestml.modelprocessor.ModelParser import ModelParser
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.ASTNESTMLCompilationUnit import ASTNESTMLCompilationUnit
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.utils.Logger import LOGGING_LEVEL, Logger

# setups the infrastructure
PredefinedUnits.registerUnits()
PredefinedTypes.registerTypes()
PredefinedFunctions.registerPredefinedFunctions()
PredefinedVariables.registerPredefinedVariables()
SymbolTable.initializeSymbolTable(ASTSourcePosition(_startLine=0, _startColumn=0, _endLine=0, _endColumn=0))
Logger.initLogger(LOGGING_LEVEL.NO)


# TODO: this is not a unit test. Don't run it with unittests or use mocks to hide filesystem, solver etc
class NESTMLTest(unittest.TestCase):
    """
    Tests if the overall model processing frontend works as intended.
    """

    def test(self):
        raise SkipTest("takes too long")
        for filename in os.listdir(os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                                 os.path.join('..', 'models')))):
            if filename.endswith(".nestml"):
                # print('Start creating AST for ' + filename + ' ...'),
                model = ModelParser.parseModel(os.path.join(os.path.dirname(__file__),
                                                            os.path.join(os.path.join('..', 'models'), filename)))
                assert (isinstance(model, ASTNESTMLCompilationUnit))
        return


if __name__ == '__main__':
    unittest.main()
