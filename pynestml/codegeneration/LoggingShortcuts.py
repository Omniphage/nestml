from pynestml.frontend.FrontendConfiguration import FrontendConfiguration
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class LoggingShortcuts(object):
    @staticmethod
    def log_start_processing_neuron(_neuron):
        # type: (ASTNeuron) -> None
        code, message = Messages.getStartProcessingNeuron(_neuron.getName())
        Logger.logMessage(_neuron=_neuron, _errorPosition=_neuron.getSourcePosition(), _code=code, _message=message,
                          _logLevel=LOGGING_LEVEL.INFO)

    @staticmethod
    def log_finished_processing_neuron(_neuron):
        # type: (ASTNeuron) -> None
        code, message = Messages.getCodeGenerated(_neuron.getName(), FrontendConfiguration.getTargetPath())
        Logger.logMessage(_neuron=_neuron, _errorPosition=_neuron.getSourcePosition(), _code=code, _message=message,
                          _logLevel=LOGGING_LEVEL.INFO)

    @staticmethod
    def log_finished_generating_module():
        # type: () -> None
        code, message = Messages.getModuleGenerated(FrontendConfiguration.getTargetPath())
        Logger.logMessage(_code=code, _message=message, _logLevel=LOGGING_LEVEL.INFO)

    @staticmethod
    def log_could_not_resolve(_name, _node):
        code, message = Messages.getCouldNotResolve(_name)
        Logger.logMessage(_code=code, _message=message,
                          _errorPosition=_node.getSourcePosition(), _logLevel=LOGGING_LEVEL.ERROR)

        pass
