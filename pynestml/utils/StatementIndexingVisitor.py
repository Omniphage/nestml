from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor


class StatementIndexingVisitor(NESTMLVisitor):

    def __init__(self):
        # type: () -> None
        super(StatementIndexingVisitor, self).__init__()
        self.result = {}

    def visit_compound_stmt(self, _stmt):
        # type: (ASTCompoundStmt) -> None
        self.result[str(_stmt)] = _stmt

    def visit_small_stmt(self, _stmt):
        # type: (ASTSmallStmt) -> None
        self.result[str(_stmt)] = _stmt

    def visit_declaration(self, _declaration):
        # type: (ASTDeclaration) -> None
        self.result[str(_declaration)] = _declaration

    @staticmethod
    def visit_node(_node):
        # type: (ASTNode) -> Dict[str,Union[ASTCompoundStmt,ASTSmallStmt,ASTDeclaration]]
        instance = StatementIndexingVisitor()
        _node.accept(instance)
        return instance.result