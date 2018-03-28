#
# CoCoBufferNotAssigned.py
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
from pynestml.modelprocessor.VariableSymbol import BlockType
from pynestml.utils.Logger import LOGGING_LEVEL, Logger
from pynestml.utils.Messages import Messages


class CoCoBufferNotAssigned(CoCo):
    """
    This coco ensures that no values are assigned to buffers.
    Allowed:
        currentSum = current + 10mV # current being a buffer
    Not allowed:
        current = currentSum + 10mV
    
    """

    @classmethod
    def checkCoCo(cls, _neuron=None):
        """
        Ensures the coco for the handed over neuron.
        :param _neuron: a single neuron instance.
        :type _neuron: ASTNeuron
        """
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.CoCo.BufferNotAssigned) No or wrong type of neuron provided (%s)!' % type(_neuron)
        _neuron.accept(NoBufferAssignedVisitor())
        return


class NoBufferAssignedVisitor(NESTMLVisitor):
    def visit_assignment(self, _assignment=None):
        try:
            symbol = _assignment.getScope().resolve_variable_symbol(_assignment.getVariable().getName())
            if (symbol.getBlockType() == BlockType.INPUT_BUFFER_SPIKE or
                    symbol.getBlockType() == BlockType.INPUT_BUFFER_CURRENT):
                code, message = Messages.getValueAssignedToBuffer(_assignment.getVariable().getCompleteName())
                Logger.logMessage(_code=code, _message=message,
                                  _errorPosition=_assignment.getSourcePosition(),
                                  _logLevel=LOGGING_LEVEL.ERROR)
        except CannotResolveSymbolError:
            LoggingShortcuts.log_could_not_resolve(_assignment.getVariable().getName(), _assignment.getVariable())
