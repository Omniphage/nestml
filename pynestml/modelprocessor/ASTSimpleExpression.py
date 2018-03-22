#
# ASTSimpleExpression.py
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
from pynestml.modelprocessor.ASTExpressionNode import ASTExpressionNode
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.ASTVariable import ASTVariable
from pynestml.modelprocessor.Either import Either


class ASTSimpleExpression(ASTExpressionNode):
    """
    This class is used to store a simple expression, e.g. +42mV.
    ASTSimpleExpression, consisting of a single element without combining operator, e.g.,10mV, inf, V_m.
    Grammar:
    simpleExpression : functionCall
                   | BOOLEAN_LITERAL // true & false;
                   | (INTEGER|FLOAT) (variable)?
                   | isInf='inf'
                   | STRING_LITERAL
                   | variable;
    Attributes:
        __functionCall (ASTFunctionCall): A function call reference.
        __numericLiteral (int or float): A numeric literal.
        __variable (ASTVariable): A variable reference.
        __isBooleanTrue (bool): True if this is a boolean true literal.
        __isBooleanFalse (bool): True if this is a boolean false literal.
        __isInf (bool): True if this is a infinity literal.
        __string (str): A string literal.
        __typeEither (Either): The type of this expreesion.

    """
    __functionCall = None
    __numericLiteral = None
    __variable = None
    __isBooleanTrue = False
    __isBooleanFalse = False
    __isInf = False
    __string = None

    def __init__(self, _functionCall=None, _booleanLiteral=None, _numericLiteral=None, _isInf=False,
                 _variable=None, _string=None, _sourcePosition=None):
        """
        Standard constructor.
        :param _functionCall: a function call.
        :type _functionCall: ASTFunctionCall
        :param _booleanLiteral: a boolean value.
        :type _booleanLiteral: bool
        :param _numericLiteral: a numeric value.
        :type _numericLiteral: float/int
        :param _isInf: is inf symbol.
        :type _isInf: bool
        :param _variable: a variable object.
        :type _variable: ASTVariable
        :param _string: a single string literal
        :type _string: str
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        """
        assert (_functionCall is None or isinstance(_functionCall, ASTFunctionCall)), \
            '(PyNestML.AST.SimpleExpression) Not a function call provided (%s)!' % type(_functionCall)
        assert (_booleanLiteral is None or isinstance(_booleanLiteral, bool)), \
            '(PyNestML.AST.SimpleExpression) Not a bool provided (%s)!' % type(_booleanLiteral)
        assert (_isInf is None or isinstance(_isInf, bool)), \
            '(PyNestML.AST.SimpleExpression) Not a bool provided (%s)!' % type(_isInf)
        assert (_variable is None or isinstance(_variable, ASTVariable)), \
            '(PyNestML.AST.SimpleExpression) Not a variable provided (%s)!' % type(_variable)
        assert (_numericLiteral is None or isinstance(_numericLiteral, int) or isinstance(_numericLiteral, float)), \
            '(PyNestML.AST.SimpleExpression) Not a number provided (%s)!' % type(_numericLiteral)
        assert (_string is None or isinstance(_string, str)), \
            '(PyNestML.AST.SimpleExpression) Not a string provided (%s)!' % type(_string)
        super(ASTSimpleExpression, self).__init__(_sourcePosition)
        self.__functionCall = _functionCall
        if _booleanLiteral is not None:
            if _booleanLiteral:
                self.__isBooleanTrue = True
            else:
                self.__isBooleanFalse = True
        self.__numericLiteral = _numericLiteral
        self.__isInf = _isInf
        self.__variable = _variable
        self.__string = _string
        return

    @classmethod
    def makeASTSimpleExpression(cls, _functionCall=None, _booleanLiteral=None, _numericLiteral=None,
                                _isInf=False, _variable=None, _string=None, _sourcePosition=None):
        """
        The factory method of the ASTSimpleExpression class.
        :param _functionCall: a function call.
        :type _functionCall: ASTFunctionCall
        :param _booleanLiteral: a boolean value.
        :type _booleanLiteral: bool
        :param _numericLiteral: a numeric value.
        :type _numericLiteral: float/int
        :param _isInf: is inf symbol.
        :type _isInf: bool
        :param _variable: a variable object.
        :type _variable: ASTVariable
        :param _sourcePosition: the position of this element in the source file.
        :type _sourcePosition: ASTSourcePosition.
        :param _string: a single string literal
        :type _string: str
        :return: a new ASTSimpleExpression object.
        :rtype: ASTSimpleExpression
        """
        return cls(_functionCall, _booleanLiteral, _numericLiteral, _isInf, _variable, _string, _sourcePosition)

    def isFunctionCall(self):
        """
        Returns whether it is a function call or not.
        :return: True if function call, otherwise False.
        :rtype: bool
        """
        return self.__functionCall is not None

    # TODO: this should really be in a common base class to ASTExpression and ASTSimpleExpression

    # TODO: this should really be in a common base class to ASTExpression and ASTSimpleExpression

    def getFunctionCall(self):
        """
        Returns the function call object.
        :return: the function call object.
        :rtype: ASTFunctionCall
        """
        return self.__functionCall

    def getFunctionCalls(self):
        """
        This function is used for better interactions with the general expression ast class.
        :return: returns a single list with this function call if such an exists, otherwise an empty list
        :rtype: list(ASTFunctionCall)
        """
        ret = list()
        if self.isFunctionCall():
            ret.append(self.getFunctionCall())
        return ret

    def isBooleanTrue(self):
        """
        Returns whether it is a boolean true literal.
        :return: True if true literal, otherwise False.
        :rtype: bool 
        """
        return self.__isBooleanTrue

    def isBooleanFalse(self):
        """
        Returns whether it is a boolean false literal.
        :return: True if false literal, otherwise False.
        :rtype: bool
        """
        return self.__isBooleanFalse

    def isNumericLiteral(self):
        """
        Returns whether it is a numeric literal or not.
        :return: True if numeric literal, otherwise False.
        :rtype: bool
        """
        return self.__numericLiteral is not None

    def getNumericLiteral(self):
        """
        Returns the value of the numeric literal.
        :return: the value of the numeric literal.
        :rtype: int/float
        """
        return self.__numericLiteral

    def isInfLiteral(self):
        """
        Returns whether it is a infinity literal or not.
        :return: True if infinity literal, otherwise False.
        :rtype: bool
        """
        return self.__isInf

    def isVariable(self):
        """
        Returns whether it is a variable or not.
        :return: True if has a variable, otherwise False.
        :rtype: bool
        """
        return self.__variable is not None and self.__numericLiteral is None

    def getVariables(self):
        """
        This function is used for better interactions with the general expression ast class.
        :return: returns a single list with this variable if such an exists, otherwise an empty list
        :rtype: list(ASTVariable)
        """
        ret = list()
        if self.isVariable():
            ret.append(self.getVariable())
        return ret

    def hasUnit(self):
        """
        Returns whether this is a numeric literal with a defined unit.
        :return: True if numeric literal with unit, otherwise False. 
        :rtype: bool
        """
        return self.__variable is not None and self.__numericLiteral is not None

    def getUnits(self):
        """
        This function is used for better interactions with the general expression ast class.
        :return: returns a single list with unit if such an exists, otherwise an empty list
        :rtype: list(ASTVariable)
        """
        ret = list()
        if self.hasUnit():
            ret.append(self.getVariable())
        return ret

    def getVariable(self):
        """
        Returns the variable.
        :return: the variable object.
        :rtype: ASTVariable
        """
        return self.__variable

    def isString(self):
        """
        Returns whether this simple expression is a string.
        :return: True if string, False otherwise.
        :rtype: bool
        """
        return self.__string is not None and isinstance(self.__string, str)

    def getString(self):
        """
        Returns the string as stored in this simple expression.
        :return: a string as stored in this expression.
        :rtype: str
        """
        return self.__string

    def getParent(self, _ast=None):
        """
        Indicates whether a this node contains the handed over node.
        :param _ast: an arbitrary ast node.
        :type _ast: AST_
        :return: AST if this or one of the child nodes contains the handed over element.
        :rtype: AST_ or None
        """
        if self.isFunctionCall():
            if self.getFunctionCall() is _ast:
                return self
            elif self.getFunctionCall().getParent(_ast) is not None:
                return self.getFunctionCall().getParent(_ast)
        if self.__variable is not None:
            if self.__variable is _ast:
                return self
            elif self.__variable.getParent(_ast) is not None:
                return self.__variable.getParent(_ast)
        return None

    def setVariable(self, _variable=None):
        """
        Updates the variable of this node.
        :param _variable: a single variable
        :type _variable: ASTVariable
        """
        assert (_variable is None or isinstance(_variable, ASTVariable)), \
            '(PyNestML.AST.SimpleExpression) No or wrong type of variable provided (%s)!' % type(_variable)
        self.__variable = _variable
        return

    def setFunctionCall(self, _functionCall):
        """
        Updates the function call of this node.
        :param _functionCall: a single function call
        :type _functionCall: ASTFunctionCall
        """
        assert (_functionCall is None or isinstance(_functionCall, ASTVariable)), \
            '(PyNestML.AST.SimpleExpression) No or wrong type of function call provided (%s)!' % type(_functionCall)
        self.__functionCall = _functionCall
        return

    def __str__(self):
        """
        Returns the string representation of the simple expression.
        :return: the operator as a string.
        :rtype: str
        """
        if self.isFunctionCall():
            return str(self.__functionCall)
        elif self.isBooleanTrue():
            return 'True'
        elif self.isBooleanFalse():
            return 'False'
        elif self.isInfLiteral():
            return 'inf'
        elif self.isNumericLiteral():
            if self.__variable is not None:
                return str(self.__numericLiteral) + str(self.__variable)
            else:
                return str(self.__numericLiteral)
        elif self.isVariable():
            return str(self.__variable)
        elif self.isString():
            return self.getString()
        else:
            raise RuntimeError('Simple expression at %s not specified!' % str(self.getSourcePosition()))

    def equals(self, _other=None):
        """
        The equals method.
        :param _other: a different object.
        :type _other: object
        :return:True if equal, otherwise False.
        :rtype: bool
        """
        if not isinstance(_other, ASTSimpleExpression):
            return False
        if self.isFunctionCall() + _other.isFunctionCall() == 1:
            return False
        if self.isFunctionCall() and _other.isFunctionCall() and not self.getFunctionCall().equals(
                _other.getFunctionCall()):
            return False
        if self.getNumericLiteral() != _other.getNumericLiteral():
            return False
        if self.isBooleanFalse() != _other.isBooleanFalse() or self.isBooleanTrue() != _other.isBooleanTrue():
            return False
        if self.isVariable() + _other.isVariable() == 1:
            return False
        if self.isVariable() and _other.isVariable() and not self.getVariable().equals(_other.getVariable()):
            return False
        if self.isInfLiteral() != _other.isInfLiteral():
            return False
        if self.isString() + _other.isString() == 1:
            return False
        if self.getString() != _other.getString():
            return False
        return True
