from copy import deepcopy

from pynestml.modelprocessor.ASTSymbolTableVisitor import ASTSymbolTableVisitor
from pynestml.solver.EquationsBlockProcessor import EquationsBlockProcessor
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class SolverOuptutIntegrator(object):
    """Integrates solved odes into a neuron"""

    @staticmethod
    def integrate_solution_into_neuron(_neuron):
        workingVersion = deepcopy(_neuron)
        workingVersion = SolverOuptutIntegrator.solveOdesAndShapes(workingVersion)
        ASTSymbolTableVisitor.update_symbol_table(workingVersion)
        return workingVersion

    @staticmethod
    def solveOdesAndShapes(_neuron):
        # it should be ensured that most one equations block is present
        equationsBlock = _neuron.getEquationsBlocks()
        if equationsBlock is None:
            return _neuron
        else:
            if len(equationsBlock.getOdeEquations()) > 1 and len(equationsBlock.getOdeShapes()) == 0:
                code, message = Messages.getNeuronSolvedBySolver(_neuron.getName())
                Logger.logMessage(_neuron=_neuron, _code=code, _message=message,
                                  _errorPosition=_neuron.getSourcePosition(), _logLevel=LOGGING_LEVEL.INFO)
                return _neuron
            else:
                code, message = Messages.getNeuronAnalyzed(_neuron.getName())
                Logger.logMessage(_neuron=_neuron, _code=code, _message=message,
                                  _errorPosition=_neuron.getSourcePosition(),
                                  _logLevel=LOGGING_LEVEL.INFO)
                workingCopy = EquationsBlockProcessor.solveOdeWithShapes(_neuron)
                return workingCopy