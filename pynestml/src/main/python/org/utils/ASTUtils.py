#
# ASTUtils.py
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
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger


class ASTUtils(object):
    """
    A collection of helpful methods.
    """

    @classmethod
    def getAllNeurons(cls, _listOfCompilationUnits=list()):
        """
        For a list of compilation units, it returns a list containing all neurons defined in all compilation
        units.
        :param _listOfCompilationUnits: a list of compilation units.
        :type _listOfCompilationUnits: list(ASTNESTMLCompilationUnit)
        :return: a list of neurons
        :rtype: list(ASTNeuron)
        """
        ret = list()
        for compiunit in _listOfCompilationUnits:
            ret.extend(compiunit.getNeuronList())
        return ret

    @classmethod
    def isSmallStmt(cls, _ast=None):
        """
        Indicates whether the handed over ast is a small statement. Used in the template.
        :param _ast: a single ast object.
        :type _ast: AST_
        :return: True if small stmt, otherwise False.
        :rtype: bool
        """
        from pynestml.src.main.python.org.nestml.ast.ASTSmallStmt import ASTSmallStmt
        return isinstance(_ast, ASTSmallStmt)

    @classmethod
    def isCompoundStmt(cls, _ast=None):
        """
        Indicates whether the handed over ast is a compound statement. Used in the template.
        :param _ast: a single ast object.
        :type _ast: AST_
        :return: True if compound stmt, otherwise False.
        :rtype: bool
        """
        from pynestml.src.main.python.org.nestml.ast.ASTCompoundStmt import ASTCompoundStmt
        return isinstance(_ast, ASTCompoundStmt)

    @classmethod
    def printComments(cls, _ast=None):
        """
        Prints all comments belonging to this node.
        :param _ast: a single ast node.
        :type _ast: AST_
        :return: all comments in the node
        :rtype: str
        """
        return "TODO comments"

    @classmethod
    def isIntegrate(cls, _functionCall=None):
        """
        Checks if the handed over function call is a ode integration function call.
        :param _functionCall: a single function call
        :type _functionCall: ASTFunctionCall
        :return: True if ode integration call, otherwise False.
        :rtype: bool
        """
        from pynestml.src.main.python.org.nestml.ast.ASTFunctionCall import ASTFunctionCall
        from pynestml.src.main.python.org.nestml.symbol_table.predefined.PredefinedFunctions import PredefinedFunctions
        assert (_functionCall is not None and isinstance(_functionCall, ASTFunctionCall)), \
            '(PyNestML.CodeGeneration.Utils) No or wrong type of function-call provided (%s)!' % type(_functionCall)
        return _functionCall.getName() == PredefinedFunctions.INTEGRATE_ODES

    @classmethod
    def isSpikeInput(cls, _body=None):
        """
        Checks if the handed over neuron contains a spike input buffer.
        :param _body: a single body element.
        :type _body: ASTBody
        :return: True if spike buffer is contained, otherwise false.
        :rtype: bool
        """
        from pynestml.src.main.python.org.nestml.ast.ASTBody import ASTBody
        assert (_body is not None and isinstance(_body, ASTBody)), \
            '(PyNestML.CodeGeneration.Utils) No or wrong type of body provided (%s)!' % type(_body)
        inputs = (inputL for block in _body.getInputBlocks() for inputL in block.getInputLines())
        for inputL in inputs:
            if inputL.isSpike():
                return True
        return False

    @classmethod
    def isCurrentInput(cls, _body=None):
        """
        Checks if the handed over neuron contains a current input buffer.
        :param _body: a single body element.
        :type _body: ASTBody
        :return: True if current buffer is contained, otherwise false.
        :rtype: bool
        """
        from pynestml.src.main.python.org.nestml.ast.ASTBody import ASTBody
        assert (_body is not None and isinstance(_body, ASTBody)), \
            '(PyNestML.CodeGeneration.Utils) No or wrong type of body provided (%s)!' % type(_body)
        inputs = (inputL for block in _body.getInputBlocks() for inputL in block.getInputLines())
        for inputL in inputs:
            if inputL.isCurrent():
                return True
        return False

    @classmethod
    def computeTypeName(cls, _dataType=None):
        """
        Computes the representation of the data type.
        :param _dataType: a single data type.
        :type _dataType: ASTDataType
        :return: the corresponding representation.
        :rtype: str
        """
        from pynestml.src.main.python.org.nestml.ast.ASTDatatype import ASTDatatype
        assert (_dataType is not None and isinstance(_dataType, ASTDatatype)), \
            '(PyNestML.CodeGeneration.Utils) No or wrong type of data type provided (%s)!' % type(_dataType)
        if _dataType.isBoolean():
            return 'boolean'
        elif _dataType.isInteger():
            return 'integer'
        elif _dataType.isReal():
            return 'real'
        elif _dataType.isString():
            return 'string'
        elif _dataType.isVoid():
            return 'void'
        elif _dataType.isUnitType():
            # TODO
            return 'TODO'
        else:
            Logger.logMessage('Type could not be derived!', LOGGING_LEVEL.ERROR)
            return ''