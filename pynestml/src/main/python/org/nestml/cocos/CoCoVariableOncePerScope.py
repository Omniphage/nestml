#
# CoCoVariableOncePerScope.py
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
from pynestml.src.main.python.org.nestml.cocos.CoCo import CoCo
from pynestml.src.main.python.org.utils.Logger import LOGGING_LEVEL, Logger


class CoCoVariableOncePerScope(CoCo):
    """
    This coco ensures that each variables is defined at most once per scope, thus no redeclaration occurs.
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Checks if each variable is defined at most once per scope. Obviously, this test does not check if a declaration
        is shadowed by an embedded scope.
        :param _neuron: a single neuron
        :type _neuron: ASTNeuron
        """
        from pynestml.src.main.python.org.nestml.ast.ASTNeuron import ASTNeuron
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo) No or wrong type of neuron provided (%s)!' % type(_neuron)
        cls.__checkScope(_neuron, _neuron.getScope())
        return

    @classmethod
    def __checkScope(cls, _neuron=None, _scope=None):
        """
        Checks a single scope and proceeds recursively.
        :param _neuron: a single neuron object, required for correct printing of messages.
        :type _neuron: ASTNeuron
        :param _scope: a single scope to check.
        :type _scope: Scope
        """
        for sym1 in _scope.getSymbolsInThisScope():  # TODO: in o(n^2), maybe a better solution is possible
            for sym2 in _scope.getSymbolsInThisScope():
                if sym1 is not sym2 and sym1.getSymbolName() == sym2.getSymbolName() and \
                                sym1.getSymbolKind() == sym2.getSymbolKind():
                    Logger.logAndPrintMessage(
                        '[' + _neuron.getName() + '.nestml] Variable %s redeclared at %s ! First declared at %s.'
                        % (sym1.getSymbolName(), sym2.getReferencedObject().getSourcePosition().printSourcePosition(),
                           sym1.getReferencedObject().getSourcePosition().printSourcePosition()), LOGGING_LEVEL.ERROR)
                    raise VariableRedeclared()
        for scope in _scope.getScopes():
            cls.__checkScope(_neuron, scope)
        return


class VariableRedeclared(Exception):
    """
    This exception is thrown whenever a variable has been re-declared in the same scope.
    """
    pass
