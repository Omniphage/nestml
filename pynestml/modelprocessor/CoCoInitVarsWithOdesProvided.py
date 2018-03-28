#
# CoCoInitVarsWithOdesProvided.py
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
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.Scope import CannotResolveSymbolError
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class CoCoInitVarsWithOdesProvided(CoCo):
    """
    This CoCo ensures that all variables which have been declared in the "initial_values" block are provided 
    with a corresponding ode.
    Allowed:
        initial_values:
            V_m mV = E_L
        end
        ...
        equations:
            V_m' = ...
        end
    Not allowed:        
        initial_values:
            V_m mV = E_L
        end
        ...
        equations:
            # no ode declaration given
        end
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Checks this coco on the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.VariablesDefined) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(InitVarsVisitor())
        return


class InitVarsVisitor(NESTMLVisitor):
    """
    This visitor checks that all variables as provided in the init block have been provided with an ode.
    """

    def visit_declaration(self, _declaration=None):
        """
        Checks the coco on the current node.
        :param _declaration: a single declaration.
        :type _declaration: ASTDeclaration
        """
        for var in _declaration.getVariables():
            try:
                symbol = _declaration.getScope().resolve_variable_symbol(var.getCompleteName())
                # first check that all initial value variables have a lhs
                if symbol.isInitValues() and not _declaration.hasExpression():
                    code, message = Messages.getNoRhs(symbol.getSymbolName())
                    Logger.logMessage(_errorPosition=var.getSourcePosition(), _code=code,
                                      _message=message, _logLevel=LOGGING_LEVEL.ERROR)
                # now check that they have been provided with an ODE
                if symbol.isInitValues() and not symbol.isOdeDefined() and not symbol.isFunction():
                    code, message = Messages.getNoOde(symbol.getSymbolName())
                    Logger.logMessage(_errorPosition=var.getSourcePosition(), _code=code,
                                      _message=message, _logLevel=LOGGING_LEVEL.ERROR)
                if symbol.isInitValues() and not symbol.hasInitialValue():
                    code, message = Messages.getNoInitValue(symbol.getSymbolName())
                    Logger.logMessage(_errorPosition=var.getSourcePosition(), _code=code,
                                      _message=message, _logLevel=LOGGING_LEVEL.ERROR)
            except CannotResolveSymbolError:
                LoggingShortcuts.log_could_not_resolve(var.getCompleteName(),var)
                return
