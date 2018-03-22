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
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.utils.Logger import LOGGING_LEVEL, Logger


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
        for compilationUnit in _listOfCompilationUnits:
            ret.extend(compilationUnit.getNeuronList())
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
        from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
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
        from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
        return isinstance(_ast, ASTCompoundStmt)

    @classmethod
    def isIntegrate(cls, _functionCall=None):
        """
        Checks if the handed over function call is a ode integration function call.
        :param _functionCall: a single function call
        :type _functionCall: ASTFunctionCall
        :return: True if ode integration call, otherwise False.
        :rtype: bool
        """
        from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
        from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
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
        from pynestml.modelprocessor.ASTBody import ASTBody
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
        from pynestml.modelprocessor.ASTBody import ASTBody
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
        from pynestml.modelprocessor.ASTDatatype import ASTDatatype
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
            return str(_dataType)
        else:
            Logger.logMessage('Type could not be derived!', LOGGING_LEVEL.ERROR)
            return ''

    @classmethod
    def getAliasSymbolsFromOdes(cls, _list=list()):
        """"
        For a handed over list this
        :param _list:
        :type _list:
        :return:
        :rtype:
        """
        pass

    @classmethod
    def getAliasSymbols(cls, _ast=None):
        """
        For the handed over ast, this method collects all functions aka. aliases in it.
        :param _ast: a single ast node
        :type _ast: AST_
        :return: a list of all alias variable symbols
        :rtype: list(VariableSymbol)
        """
        assert (_ast is not None), '(PyNestML.Utils) No AST provided!'
        ret = list()
        from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
        from pynestml.modelprocessor.ASTVariable import ASTVariable
        res = list()
        higher_order_visitor = ASTHigherOrderVisitor(lambda x: res.append(x) if isinstance(x, ASTVariable) else True)
        _ast.accept(higher_order_visitor)
        for var in res:
            if '\'' not in var.getCompleteName():
                symbol = _ast.getScope().resolveToSymbol(var.getCompleteName(), SymbolKind.VARIABLE)
                if symbol.isFunction():
                    ret.append(symbol)
        return ret

    @classmethod
    def getAll(cls, _ast=None, _type=None):
        """
        Finds all ast which are part of the tree as spanned by the handed over ast. The type has to be specified.
        :param _ast: a single ast node
        :type _ast: AST_
        :param _type: the type
        :type _type: AST_
        :return: a list of all ast of the specified type
        :rtype: list(AST_)
        """
        from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
        ret = list()
        higher_order_visitor = ASTHigherOrderVisitor(lambda x: ret.append(x) if isinstance(x, _type) else True)
        _ast.accept(higher_order_visitor)
        return ret

    @classmethod
    def getVectorizedVariable(cls, _ast=None, _scope=None):
        """
        Returns all variable symbols which are contained in the scope and have a size parameter.
        :param _ast: a single ast
        :type _ast: AST_
        :param _scope: a scope object
        :type _scope: Scope
        :return: the first element with the size parameter
        :rtype: VariableSymbol
        """
        from pynestml.modelprocessor.ASTVariable import ASTVariable
        from pynestml.modelprocessor.Symbol import SymbolKind
        variables = (var for var in cls.getAll(_ast, ASTVariable) if
                     _scope.resolveToSymbol(var.getCompleteName(), SymbolKind.VARIABLE))
        for var in variables:
            symbol = _scope.resolveToSymbol(var.getCompleteName(), SymbolKind.VARIABLE)
            if symbol is not None and symbol.hasVectorParameter():
                return symbol
        return None

    @classmethod
    def getFunctionCall(cls, _ast=None, _functionName=None):
        """
        Collects for a given name all function calls in a given ast node.
        :param _ast: a single node
        :type _ast: AST_
        :param _functionName:
        :type _functionName:
        :return: a list of all function calls contained in _ast
        :rtype: list(ASTFunctionCall)
        """
        from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
        from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
        ret = list()
        higher_order_visitor= ASTHigherOrderVisitor(lambda x: ret.append(x) if isinstance(x, ASTFunctionCall) and x.getName() == _functionName else True)
        _ast.accept(higher_order_visitor)
        return ret

    @classmethod
    def getTupleFromSingleDictEntry(cls, _dictEntry=None):
        """
        For a given dict of length 1, this method returns a tuple consisting of (key,value)
        :param _dictEntry: a dict of length 1
        :type _dictEntry:  dict
        :return: a single tuple
        :rtype: tuple
        """
        if len(_dictEntry.keys()) == 1:
            # key() is not an actual list, thus indexing is not possible.
            for keyIter in _dictEntry.keys():
                key = keyIter
                value = _dictEntry[key]
                return key, value
        else:
            return None, None

    @classmethod
    def needsArguments(cls, _astFunctionCall):
        """
        Indicates whether a given function call has any arguments
        :param _astFunctionCall: a function call
        :type _astFunctionCall: ASTFunctionCall
        :return: True if arguments given, otherwise false
        :rtype: bool
        """
        from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
        assert (_astFunctionCall is not None and isinstance(_astFunctionCall, ASTFunctionCall))
        return len(_astFunctionCall.getArgs()) > 0
