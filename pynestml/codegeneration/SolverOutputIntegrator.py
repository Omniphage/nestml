from copy import deepcopy

from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTSymbolTableVisitor import ASTSymbolTableVisitor
from pynestml.solver.EquationsBlockProcessor import EquationsBlockProcessor
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class SolverOutputIntegrator(object):
    """Integrates solved odes into a neuron"""

    @staticmethod
    def integrate_solution_into_neuron(_neuron):
        # type: (ASTNeuron) -> ASTNeuron
        working_version = deepcopy(_neuron)
        working_version = SolverOutputIntegrator.solve_odes_and_shapes(working_version)
        ASTSymbolTableVisitor.update_symbol_table(working_version)
        return working_version

    @staticmethod
    def solve_odes_and_shapes(_neuron):
        # type: (ASTNeuron) -> ASTNeuron
        # it should be ensured that most one equations block is present
        equations_block = _neuron.getEquationsBlocks()
        if equations_block is None:
            return _neuron
        else:
            if len(equations_block.getOdeEquations()) > 1 and len(equations_block.getOdeShapes()) == 0:
                code, message = Messages.getNeuronSolvedBySolver(_neuron.getName())
                Logger.logMessage(_neuron=_neuron, _code=code, _message=message,
                                  _errorPosition=_neuron.getSourcePosition(), _logLevel=LOGGING_LEVEL.INFO)
                return _neuron
            else:
                code, message = Messages.getNeuronAnalyzed(_neuron.getName())
                Logger.logMessage(_neuron=_neuron, _code=code, _message=message,
                                  _errorPosition=_neuron.getSourcePosition(),
                                  _logLevel=LOGGING_LEVEL.INFO)
                working_copy = EquationsBlockProcessor.solveOdeWithShapes(_neuron)
                return working_copy
