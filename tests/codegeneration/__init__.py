from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedUnits import PredefinedUnits
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.SymbolTable import SymbolTable


def setup():
    # type: () -> None
    PredefinedUnits.registerUnits()
    PredefinedTypes.registerTypes()
    PredefinedVariables.registerPredefinedVariables()
    PredefinedFunctions.registerPredefinedFunctions()
    SymbolTable.initializeSymbolTable(ASTSourcePosition())
