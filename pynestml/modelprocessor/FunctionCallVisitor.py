#
# FunctionCallVisitor.py
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
"""
simpleExpression : functionCall
"""
from pynestml.codegeneration.LoggingShortcuts import LoggingShortcuts
from pynestml.modelprocessor.ErrorStrings import ErrorStrings
from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.Scope import CannotResolveSymbolError
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.VoidTypeSymbol import VoidTypeSymbol
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class FunctionCallVisitor(NESTMLVisitor):
    """
    Visits a single function call and updates its type.
    """

    def visit_simple_expression(self, _expr=None):
        """
        Visits a single function call as stored in a simple expression and derives the correct type of all its
        parameters. :param _expr: a simple expression :type _expr: ASTSimpleExpression :rtype void
        """
        scope = _expr.getScope()
        function_name = _expr.getFunctionCall().getName()
        try:
            method_symbol = scope.resolve_function_symbol(function_name)
        # check if this function exists
        except CannotResolveSymbolError:
            code, message = Messages.getCouldNotResolve(function_name)
            Logger.logMessage(_code=code, _message=message, _errorPosition=_expr.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
            _expr.type = ErrorTypeSymbol()
            return
        return_type = method_symbol.getReturnType()
        return_type.referenced_object = _expr

        # convolve symbol does not have a return type set.
        # returns whatever type the second parameter is.
        if function_name == PredefinedFunctions.CONVOLVE:
            # Deviations from the assumptions made here are handled in the convolveCoco
            buffer_parameter = _expr.getFunctionCall().getArgs()[1]

            if buffer_parameter.getVariable() is not None:
                buffer_name = buffer_parameter.getVariable().getName()
                try:
                    buffer_symbol = scope.resolve_variable_symbol(buffer_name)
                    _expr.type = buffer_symbol.getTypeSymbol()
                    return
                except CannotResolveSymbolError:
                    LoggingShortcuts.log_could_not_resolve(buffer_name, buffer_parameter.getVariable())


            # getting here means there is an error with the parameters to convolve
            code, message = Messages.get_convolve_needs_buffer_parameter()
            Logger.logMessage(_code=code, _message=message, _errorPosition=_expr.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
            _expr.type = ErrorTypeSymbol()
            return

        if isinstance(method_symbol.getReturnType(), VoidTypeSymbol):
            error_msg = ErrorStrings.messageVoidFunctionOnRhs(self, function_name, _expr.getSourcePosition())
            _expr.type = ErrorTypeSymbol()
            return

        # if nothing special is handled, just get the expression type from the return type of the function
        _expr.type = return_type
