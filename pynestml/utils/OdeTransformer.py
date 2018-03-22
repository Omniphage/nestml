#
# OdeTransformer.py
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
from copy import copy

from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions


class OdeTransformer(object):
    """
    This class contains several methods as used to transform ODEs.
    """
    __functions = (PredefinedFunctions.CURR_SUM, PredefinedFunctions.COND_SUM, PredefinedFunctions.CONVOLVE,
                   PredefinedFunctions.BOUNDED_MAX, PredefinedFunctions.BOUNDED_MIN)
    __sumFunctions = (PredefinedFunctions.CURR_SUM, PredefinedFunctions.COND_SUM, PredefinedFunctions.CONVOLVE)

    @classmethod
    def replaceFunctions(cls, _ast):
        """
        Replaces all self.function in the handed over node.
        :param _ast: a single ast node.
        :type _ast: AST_
        """
        workingCopy = copy(_ast)
        functionCalls = cls.getFunctionCalls(workingCopy, cls.__functions)
        for call in functionCalls:
            cls.replaceFunctionCallThroughFirstArgument(workingCopy, call)
        return workingCopy

    @classmethod
    def replaceSumCalls(cls, _ast):
        """
        Replaces all sum calls in the handed over node.
        :param _ast: a single node
        :type _ast: AST_
        """
        assert (_ast is not None), '(PyNestML.Utils) No ast provided!'
        workingCopy = copy(_ast)
        functionCalls = cls.get_sumFunctionCalls(workingCopy)
        for call in functionCalls:
            cls.replaceFunctionCallThroughFirstArgument(workingCopy, call)
        return _ast

    @classmethod
    def replaceFunctionCallThroughFirstArgument(cls, _ast=None, _toReplace=None):
        """
        Replaces all occurrences of the handed over function call by the first argument.
        :param _ast: a single ast node
        :type _ast: AST_
        :param _toReplace: the function to replace
        :type _toReplace: ASTFunctionCall
        """

        # we define a local collection operation
        def replaceFunctionCallThroughFirstArgument(_expr=None):
            if _expr.isFunctionCall() and _expr.getFunctionCall() == _toReplace:
                firstArg = _expr.getFunctionCall().getArgs()[0].getVariable()
                _expr.setFunctionCall(None)
                _expr.setVariable(firstArg)
            return

        from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
        from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
        higher_order_visitor = ASTHigherOrderVisitor(
            lambda x: replaceFunctionCallThroughFirstArgument(x) if isinstance(x, ASTSimpleExpression) else True)
        _ast.accept(higher_order_visitor)
        return

    @classmethod
    def get_sumFunctionCalls(cls, _ast=None):
        """
        Returns all sum function calls in the handed over ast node or one of its children.
        :param _ast: a single ast node.
        :type _ast: AST_
        """
        return cls.getFunctionCalls(_ast, cls.__sumFunctions)

    @classmethod
    def containsSumFunctionCall(cls, _ast):
        """
        Indicates whether _ast or one of its child nodes contains a sum call.
        :param _ast: a single ast
        :type _ast: AST_
        :return: True if sum is contained, otherwise False.
        :rtype: bool
        """
        return len(cls.getFunctionCalls(_ast, cls.__sumFunctions)) > 0

    @classmethod
    def getFunctionCalls(cls, _astNode=None, _functionList=list()):
        """
        For a handed over list of function names, this method retrieves all functions in the ast.
        :param _astNode: a single ast node
        :type _astNode: AST_
        :param _functionList: a list of function names
        :type _functionList: list(str)
        :return: a list of all functions in the ast
        :rtype: list(ASTFunctionCall)
        """
        res = list()
        from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
        from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
        higher_order_visitor = ASTHigherOrderVisitor(
            lambda x: res.append(x) if isinstance(x, ASTFunctionCall) and x.getName() in _functionList else True)
        _astNode.accept(higher_order_visitor)
        return res

    @classmethod
    def getCondSumFunctionCall(cls, _astNode=None):
        """
        Collects all cond_sum function calls in the ast.
        :param _astNode: a single ast node
        :type _astNode: AST_
        :return: a list of all functions in the ast
        :rtype: list(ASTFunctionCall)
        """
        res = list()
        from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
        from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall

        higher_order_visitor = ASTHigherOrderVisitor(lambda x: res.append(x) if isinstance(x, ASTFunctionCall) and
                                                                         x.getName() == PredefinedFunctions.COND_SUM
        else True)
        _astNode.accept(higher_order_visitor)
        return res
