#
# CoCoAllFunctionsDeclared.py
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
from pynestml.codegeneration.LoggingShortcuts import LoggingShortcuts
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.CoCo import CoCo
from pynestml.modelprocessor.ErrorTypeSymbol import ErrorTypeSymbol
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.Scope import CannotResolveSymbolError
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.TypeCaster import TypeCaster
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class CoCoFunctionCallsConsistent(CoCo):
    """
    This coco ensures that for all function calls in the handed over neuron, the corresponding function is 
    defined and the types of arguments in the function call correspond to the one in the function symbol.
    Not allowed:
        maximum integer = max(1,2,3)
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Checks the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.FunctionCallsConsistent) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(FunctionCallConsistencyVisitor())
        return


class FunctionCallConsistencyVisitor(NESTMLVisitor):
    """
    This visitor ensures that all function calls are consistent.
    """

    def visit_function_call(self, _functionCall=None):
        """
        Checks the coco.
        :param _functionCall: a single function call.
        :type _functionCall: ASTFunctionCall
        """
        funcName = _functionCall.getName()
        if funcName == 'convolve' or funcName == 'cond_sum' or funcName == 'curr_sum':
            return
        # now, for all expressions, check for all function calls, the corresponding function is declared.
        try:
            symbol = _functionCall.getScope().resolve_function_symbol(_functionCall.getName())
            # now check if the number of arguments is the same as in the symbol
            if len(_functionCall.getArgs()) != len(symbol.getParameterTypes()):
                code, message = Messages.getWrongNumberOfArgs(str(_functionCall), len(symbol.getParameterTypes()),
                                                              len(_functionCall.getArgs()))
                Logger.logMessage(_code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR,
                                  _errorPosition=_functionCall.getSourcePosition())
            # finally check if the call is correctly typed
            else:
                expectedTypes = symbol.getParameterTypes()
                actualTypes = _functionCall.getArgs()
                for i in range(0, len(actualTypes)):
                    expectedType = expectedTypes[i]
                    actual_type = actualTypes[i].type
                    if isinstance(actual_type, ErrorTypeSymbol):
                        code, message = Messages.getTypeCouldNotBeDerived(actualTypes[i])
                        Logger.logMessage(_code=code, _message=message, _logLevel=LOGGING_LEVEL.ERROR,
                                          _errorPosition=actualTypes[i].getSourcePosition())
                        return
                    if not actual_type.equals(expectedType):
                        TypeCaster.try_to_recover_or_error(expectedType, actual_type, actualTypes[i])

        # first check if the function has been declared
        except CannotResolveSymbolError:
            LoggingShortcuts.log_could_not_resolve(_functionCall.getName(),_functionCall)
            return