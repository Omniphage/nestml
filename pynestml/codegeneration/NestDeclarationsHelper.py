#
# NestDeclarationsHelper.py
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
from typing import List

from pynestml.codegeneration.PyNestMl2NESTTypeConverter import NESTML2NESTTypeConverter
from pynestml.modelprocessor.ASTDeclaration import ASTDeclaration
from pynestml.modelprocessor.Symbol import SymbolKind
from pynestml.modelprocessor.TypeSymbol import TypeSymbol
from pynestml.modelprocessor.VariableSymbol import VariableSymbol
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages


class NestDeclarationsHelper(object):
    """
    This class contains several methods as used during generation of code.
    """
    nestml2NESTTypeConverter = None

    def __init__(self):
        # type: () -> None
        self.nestml2NESTTypeConverter = NESTML2NESTTypeConverter()
        return

    @staticmethod
    def get_variables(_ast_declaration=None):
        # type: (ASTDeclaration) ->List[VariableSymbol]
        ret = list()
        for var in _ast_declaration.getVariables():
            symbol = _ast_declaration.getScope().resolveToSymbol(var.getCompleteName(), SymbolKind.VARIABLE)
            if symbol is not None:
                ret.append(symbol)
            else:
                code, message = Messages.getCouldNotResolve(var.getCompleteName())
                Logger.logMessage(_code=code, _message=message,
                                  _errorPosition=_ast_declaration.getSourcePosition(), _logLevel=LOGGING_LEVEL.ERROR)
            return ret

    def print_variable_type(self, _variable_symbol=None):
        # type: (VariableSymbol) -> str
        if _variable_symbol.hasVectorParameter():
            return 'std::vector< ' + self.nestml2NESTTypeConverter.convert(_variable_symbol.getTypeSymbol()) + ' > '
        else:
            return self.nestml2NESTTypeConverter.convert(_variable_symbol.getTypeSymbol())

    @staticmethod
    def print_size_parameter(_ast_declaration=None):
        # type: (ASTDeclaration) -> str
        return _ast_declaration.getSizeParameter()

    def get_domain_from_type(self, _type_symbol=None):
        # type: (TypeSymbol) -> str
        return self.nestml2NESTTypeConverter.convert(_type_symbol)
