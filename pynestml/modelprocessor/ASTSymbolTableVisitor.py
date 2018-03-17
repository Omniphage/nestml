#
# ASTSymbolTableVisitor.py
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
from pynestml.modelprocessor.CoCosManager import CoCosManager
from pynestml.modelprocessor.Either import Either
from pynestml.modelprocessor.FunctionSymbol import FunctionSymbol
from pynestml.modelprocessor.ModelVisitor import NESTMLVisitor
from pynestml.modelprocessor.PredefinedFunctions import PredefinedFunctions
from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
from pynestml.modelprocessor.PredefinedVariables import PredefinedVariables
from pynestml.modelprocessor.Scope import Scope, ScopeType
from pynestml.modelprocessor.VariableSymbol import VariableSymbol, BlockType, VariableType
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class ASTSymbolTableVisitor(NESTMLVisitor):
    """
    This class is used to create a symbol table from a handed over AST.
    
    Attributes:
        __currentBlockType This variable is used to store information regarding which block with declarations is 
                            currently visited. It is used to update the BlockType of variable symbols to the correct
                            element.
    """
    __currentBlockType = None

    @classmethod
    def update_symbol_table(cls, _ast_neuron=None):
        """
        Creates for the handed over ast the corresponding symbol table.
        :param _ast_neuron: a AST neuron object as used to create the symbol table
        :type _ast_neuron: ASTNeuron
        :return: a new symbol table
        :rtype: SymbolTable
        """
        Logger.setCurrentNeuron(_ast_neuron)
        code, message = Messages.getStartBuildingSymbolTable()
        Logger.logMessage(_neuron=_ast_neuron, _code=code, _errorPosition=_ast_neuron.getSourcePosition(),
                          _message=message, _logLevel=LOGGING_LEVEL.INFO)
        ASTSymbolTableVisitor.visit_neuron(_ast_neuron)
        Logger.setCurrentNeuron(None)
        return

    @classmethod
    def visit_neuron(cls, _neuron=None):
        """
        Private method: Used to visit a single neuron and create the corresponding global as well as local scopes.
        :return: a single neuron.
        :rtype: ASTNeuron
        """
        from pynestml.modelprocessor.ASTNeuron import ASTNeuron
        assert (_neuron is not None and isinstance(_neuron, ASTNeuron)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of neuron provided (%s)!' % type(_neuron)
        # before starting the work on the neuron, make everything which was implicit explicit
        # but if we have a model without an equations block, just skip this step
        if _neuron.getEquationsBlocks() is not None:
            cls.make_implicit_odes_explicit(_neuron.getEquationsBlocks())
        scope = Scope(_scopeType=ScopeType.GLOBAL, _sourcePosition=_neuron.getSourcePosition())
        _neuron.updateScope(scope)
        _neuron.getBody().updateScope(scope)
        # now first, we add all predefined elements to the scope
        variables = PredefinedVariables.getVariables()
        functions = PredefinedFunctions.getFunctionSymbols()
        for symbol in variables.keys():
            _neuron.getScope().addSymbol(variables[symbol])
        for symbol in functions.keys():
            _neuron.getScope().addSymbol(functions[symbol])
        # now create the actual scope
        cls.visit_body(_neuron.getBody())
        # before following checks occur, we need to ensure several simple properties
        CoCosManager.postSymbolTableBuilderChecks(_neuron)
        # the following part is done in order to mark conductance based buffers as such.
        if _neuron.getInputBlocks() is not None and _neuron.getEquationsBlocks() is not None and \
                len(_neuron.getEquationsBlocks().getDeclarations()) > 0:
            # this case should be prevented, since several input blocks result in  a incorrect model
            if isinstance(_neuron.getInputBlocks(), list):
                buffers = (buffer for bufferA in _neuron.getInputBlocks() for buffer in bufferA.getInputLines())
            else:
                buffers = (buffer for buffer in _neuron.getInputBlocks().getInputLines())
            from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape

            cls.mark_conductance_based_buffers(buffers)
        # now update the equations
        if _neuron.getEquationsBlocks() is not None and len(_neuron.getEquationsBlocks().getDeclarations()) > 0:
            equation_block = _neuron.getEquationsBlocks()
            cls.assign_ode_to_variables(equation_block)
        CoCosManager.postOdeSpecificationChecks(_neuron)
        return

    @classmethod
    def visit_body(cls, _body=None):
        """
        Private method: Used to visit a single neuron body and create the corresponding scope.
        :param _body: a single body element.
        :type _body: ASTBody
        """
        from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
        from pynestml.modelprocessor.ASTUpdateBlock import ASTUpdateBlock
        from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
        from pynestml.modelprocessor.ASTInputBlock import ASTInputBlock
        from pynestml.modelprocessor.ASTOutputBlock import ASTOutputBlock
        from pynestml.modelprocessor.ASTFunction import ASTFunction
        for bodyElement in _body.getBodyElements():
            bodyElement.updateScope(_body.getScope())
            if isinstance(bodyElement, ASTBlockWithVariables):
                cls.visit_block_with_variables(bodyElement)
            elif isinstance(bodyElement, ASTUpdateBlock):
                cls.visit_update_block(bodyElement)
            elif isinstance(bodyElement, ASTEquationsBlock):
                cls.visit_equations_block(bodyElement)
            elif isinstance(bodyElement, ASTInputBlock):
                cls.visit_input_block(bodyElement)
            elif isinstance(bodyElement, ASTOutputBlock):
                cls.visit_output_block(bodyElement)
            elif isinstance(bodyElement, ASTFunction):
                cls.visit_function_block(bodyElement)
        return

    @classmethod
    def visit_function_block(cls, _block=None):
        """
        Private method: Used to visit a single function block and create the corresponding scope.
        :param _block: a function block object.
        :type _block: ASTFunction
        """
        from pynestml.modelprocessor.ASTFunction import ASTFunction
        from pynestml.modelprocessor.ASTUnitTypeVisitor import ASTUnitTypeVisitor
        assert (_block is not None and isinstance(_block, ASTFunction)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of function block provided (%s)!' % type(_block)
        cls.__currentBlockType = BlockType.LOCAL  # before entering, update the current block type
        symbol = FunctionSymbol(_scope=_block.getScope(), _referenced_object=_block, _paramTypes=list(),
                                _name=_block.getName(), _isPredefined=False)
        symbol.setComment(_block.getComment())
        _block.getScope().addSymbol(symbol)
        scope = Scope(_scopeType=ScopeType.FUNCTION, _enclosingScope=_block.getScope(),
                      _sourcePosition=_block.getSourcePosition())
        _block.getScope().addScope(scope)
        for arg in _block.getParameters():
            # first visit the data type to ensure that variable symbol can receive a combined data type
            arg.getDataType().updateScope(scope)
            cls.visit_data_type(arg.getDataType())
            # given the fact that the name is not directly equivalent to the one as stated in the model,
            # we have to get it by the sub-visitor
            type_name = ASTUnitTypeVisitor.visitDatatype(arg.getDataType())
            # first collect the types for the parameters of the function symbol
            symbol.addParameterType(PredefinedTypes.getTypeIfExists(type_name))
            # update the scope of the arg
            arg.updateScope(scope)
            # create the corresponding variable symbol representing the parameter
            var_symbol = VariableSymbol(_referenced_object=arg, _scope=scope, _name=arg.getName(),
                                        _blockType=BlockType.LOCAL, _isPredefined=False, _isFunction=False,
                                        _isRecordable=False,
                                        _typeSymbol=PredefinedTypes.getTypeIfExists(type_name),
                                        _variableType=VariableType.VARIABLE)
            scope.addSymbol(var_symbol)
        if _block.hasReturnType():
            _block.get_return_data_type().updateScope(scope)
            cls.visit_data_type(_block.get_return_data_type())
            symbol.setReturnType(
                PredefinedTypes.getTypeIfExists(ASTUnitTypeVisitor.visitDatatype(_block.get_return_data_type())))
        else:
            symbol.setReturnType(PredefinedTypes.getVoidType())
        _block.getBlock().updateScope(scope)
        cls.visit_block(_block.getBlock())
        cls.__currentBlockType = None  # before leaving update the type
        return

    @classmethod
    def visit_update_block(cls, _block=None):
        """
        Private method: Used to visit a single update block and create the corresponding scope.
        :param _block: an update block object.
        :type _block: ASTDynamics
        """
        from pynestml.modelprocessor.ASTUpdateBlock import ASTUpdateBlock
        assert (_block is not None and isinstance(_block, ASTUpdateBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of update-block provided (%s)!' % type(_block)
        cls.__currentBlockType = BlockType.LOCAL
        scope = Scope(_scopeType=ScopeType.UPDATE, _enclosingScope=_block.getScope(),
                      _sourcePosition=_block.getSourcePosition())
        _block.getScope().addScope(scope)
        _block.getBlock().updateScope(scope)
        cls.visit_block(_block.getBlock())
        cls.__currentBlockType = BlockType.LOCAL
        return

    @classmethod
    def visit_block(cls, _block=None):
        """
        Private method: Used to visit a single block of statements, create and update the corresponding scope.
        :param _block: a block object.
        :type _block: ASTBlock
        """
        from pynestml.modelprocessor.ASTBlock import ASTBlock
        from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
        from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
        assert (_block is not None and isinstance(_block, ASTBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of block provided %s!' % type(_block)
        for stmt in _block.getStmts():
            if isinstance(stmt, ASTSmallStmt):
                stmt.updateScope(_block.getScope())
                cls.visit_small_stmt(stmt)
            elif isinstance(stmt, ASTCompoundStmt):
                stmt.updateScope(_block.getScope())
                cls.visit_compound_stmt(stmt)
        return

    @classmethod
    def visit_small_stmt(cls, _stmt=None):
        """
        Private method: Used to visit a single small statement and create the corresponding sub-scope.
        :param _stmt: a single small statement.
        :type _stmt: ASTSmallStatement
        """
        from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
        assert (_stmt is not None and isinstance(_stmt, ASTSmallStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of small statement provided (%s)!' % type(_stmt)
        if _stmt.isDeclaration():
            _stmt.getDeclaration().updateScope(_stmt.getScope())
            cls.visit_declaration(_stmt.getDeclaration())
        elif _stmt.isAssignment():
            _stmt.getAssignment().updateScope(_stmt.getScope())
            cls.visit_assignment(_stmt.getAssignment())
        elif _stmt.isFunctionCall():
            _stmt.getFunctionCall().updateScope(_stmt.getScope())
            cls.visit_function_call(_stmt.getFunctionCall())
        elif _stmt.isReturnStmt():
            _stmt.getReturnStmt().updateScope(_stmt.getScope())
            cls.visit_return_stmt(_stmt.getReturnStmt())
        return

    @classmethod
    def visit_compound_stmt(cls, _stmt=None):
        """
        Private method: Used to visit a single compound statement and create the corresponding sub-scope.
        :param _stmt: a single compound statement.
        :type _stmt: ASTCompoundStatement
        """
        from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
        assert (_stmt is not None and isinstance(_stmt, ASTCompoundStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of compound statement provided (%s)!' % type(_stmt)
        if _stmt.isIfStmt():
            _stmt.getIfStmt().updateScope(_stmt.getScope())
            cls.visit_if_stmt(_stmt.getIfStmt())
        elif _stmt.isWhileStmt():
            _stmt.getWhileStmt().updateScope(_stmt.getScope())
            cls.visit_while_stmt(_stmt.getWhileStmt())
        else:
            _stmt.getForStmt().updateScope(_stmt.getScope())
            cls.visit_for_stmt(_stmt.getForStmt())
        return

    @classmethod
    def visit_assignment(cls, _assignment=None):
        """
        Private method: Used to visit a single assignment and update the its corresponding scope.
        :param _assignment: an assignment object.
        :type _assignment: ASTAssignment
        :return: no return value, since neither scope nor symbol is created
        :rtype: void
        """
        from pynestml.modelprocessor.ASTAssignment import ASTAssignment
        assert (_assignment is not None and isinstance(_assignment, ASTAssignment)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of assignment provided (%s)!' % type(_assignment)
        _assignment.getVariable().updateScope(_assignment.getScope())
        cls.visit_variable(_assignment.getVariable())
        _assignment.getExpression().updateScope(_assignment.getScope())
        cls.visit_expression(_assignment.getExpression())
        return

    @classmethod
    def visit_function_call(cls, _function_call=None):
        """
        Private method: Used to visit a single function call and update its corresponding scope.
        :param _function_call: a function call object.
        :type _function_call: ASTFunctionCall
        :return: no return value, since neither scope nor symbol is created
        :rtype: void
        """
        from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
        assert (_function_call is not None and isinstance(_function_call, ASTFunctionCall)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of function call provided (%s)!' % type(_function_call)
        for arg in _function_call.getArgs():
            arg.updateScope(_function_call.getScope())
            cls.visit_expression(arg)
        return

    @classmethod
    def visit_declaration(cls, _declaration=None):
        """
        Private method: Used to visit a single declaration, update its scope and return the corresponding set of
        symbols
        :param _declaration: a declaration object.
        :type _declaration: ASTDeclaration
        :return: the scope is update without a return value.
        :rtype: void
        """
        from pynestml.modelprocessor.ASTDeclaration import ASTDeclaration
        from pynestml.modelprocessor.VariableSymbol import VariableSymbol, BlockType, VariableType
        from pynestml.modelprocessor.ASTUnitTypeVisitor import ASTUnitTypeVisitor
        assert (_declaration is not None and isinstance(_declaration, ASTDeclaration)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong typ of declaration provided (%s)!' % type(_declaration)

        expression = _declaration.getExpression() if _declaration.hasExpression() else None
        type_name = ASTUnitTypeVisitor.visitDatatype(_declaration.getDataType())
        # all declarations in the state block are recordable
        is_recordable = _declaration.isRecordable() or \
            cls.__currentBlockType == BlockType.STATE or cls.__currentBlockType == BlockType.INITIAL_VALUES
        init_value = _declaration.getExpression() if cls.__currentBlockType == BlockType.INITIAL_VALUES else None
        vector_parameter = _declaration.getSizeParameter()
        for var in _declaration.getVariables():  # for all variables declared create a new symbol
            var.updateScope(_declaration.getScope())
            type_symbol = PredefinedTypes.getTypeIfExists(type_name)
            symbol = VariableSymbol(_referenced_object=_declaration,
                                    _scope=_declaration.getScope(),
                                    _name=var.getCompleteName(),
                                    _blockType=cls.__currentBlockType,
                                    _declaringExpression=expression, _isPredefined=False,
                                    _isFunction=_declaration.isFunction(),
                                    _isRecordable=is_recordable,
                                    _typeSymbol=type_symbol,
                                    _initialValue=init_value,
                                    _vectorParameter=vector_parameter,
                                    _variableType=VariableType.VARIABLE
                                    )
            symbol.setComment(_declaration.getComment())
            _declaration.getScope().addSymbol(symbol)
            var.setTypeSymbol(Either.value(type_symbol))
            cls.visit_variable(var)
        _declaration.getDataType().updateScope(_declaration.getScope())
        cls.visit_data_type(_declaration.getDataType())
        if _declaration.hasExpression():
            _declaration.getExpression().updateScope(_declaration.getScope())
            cls.visit_expression(_declaration.getExpression())
        if _declaration.hasInvariant():
            _declaration.getInvariant().updateScope(_declaration.getScope())
            cls.visit_expression(_declaration.getInvariant())
        return

    @classmethod
    def visit_return_stmt(cls, _return_stmt=None):
        """
        Private method: Used to visit a single return statement and update its scope.
        :param _return_stmt: a return statement object.
        :type _return_stmt: ASTReturnStmt
        """
        from pynestml.modelprocessor.ASTReturnStmt import ASTReturnStmt
        assert (_return_stmt is not None and isinstance(_return_stmt, ASTReturnStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of return statement provided (%s)!' % type(_return_stmt)
        if _return_stmt.hasExpression():
            _return_stmt.getExpression().updateScope(_return_stmt.getScope())
            cls.visit_expression(_return_stmt.getExpression())
        return

    @classmethod
    def visit_if_stmt(cls, _if_stmt=None):
        """
        Private method: Used to visit a single if-statement, update its scope and create the corresponding sub-scope.
        :param _if_stmt: an if-statement object.
        :type _if_stmt: ASTIfStmt
        """
        from pynestml.modelprocessor.ASTIfStmt import ASTIfStmt
        assert (_if_stmt is not None and isinstance(_if_stmt, ASTIfStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of if-statement provided (%s)!' % type(_if_stmt)
        _if_stmt.getIfClause().updateScope(_if_stmt.getScope())
        cls.visit_if_clause(_if_stmt.getIfClause())
        for elIf in _if_stmt.getElifClauses():
            elIf.updateScope(_if_stmt.getScope())
            cls.visit_elif_clause(elIf)
        if _if_stmt.hasElseClause():
            _if_stmt.getElseClause().updateScope(_if_stmt.getScope())
            cls.visit_else_clause(_if_stmt.getElseClause())
        return

    @classmethod
    def visit_if_clause(cls, _if_clause=None):
        """
        Private method: Used to visit a single if-clause, update its scope and create the corresponding sub-scope.
        :param _if_clause: an if clause.
        :type _if_clause: ASTIfClause
        """
        from pynestml.modelprocessor.ASTIfClause import ASTIfClause
        assert (_if_clause is not None and isinstance(_if_clause, ASTIfClause)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of if-clause provided (%s)!' % type(_if_clause)
        _if_clause.getCondition().updateScope(_if_clause.getScope())
        cls.visit_expression(_if_clause.getCondition())
        _if_clause.getBlock().updateScope(_if_clause.getScope())
        cls.visit_block(_if_clause.getBlock())
        return

    @classmethod
    def visit_elif_clause(cls, _elif_clause=None):
        """
        Private method: Used to visit a single elif-clause, update its scope and create the corresponding sub-scope.
        :param _elif_clause: an elif clause.
        :type _elif_clause: ASTElifClause
        """
        from pynestml.modelprocessor.ASTElifClause import ASTElifClause
        assert (_elif_clause is not None and isinstance(_elif_clause, ASTElifClause)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of elif-clause provided (%s)!' % type(_elif_clause)
        _elif_clause.getCondition().updateScope(_elif_clause.getScope())
        cls.visit_expression(_elif_clause.getCondition())
        _elif_clause.getBlock().updateScope(_elif_clause.getScope())
        cls.visit_block(_elif_clause.getBlock())
        return

    @classmethod
    def visit_else_clause(cls, _else_clause=None):
        """
        Private method: Used to visit a single else-clause, update its scope and create the corresponding sub-scope.
        :param _else_clause: an else clause.
        :type _else_clause: ASTElseClause
        """
        from pynestml.modelprocessor.ASTElseClause import ASTElseClause
        assert (_else_clause is not None and isinstance(_else_clause, ASTElseClause)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of else-clause provided (%s)!' % type(_else_clause)
        _else_clause.getBlock().updateScope(_else_clause.getScope())
        cls.visit_block(_else_clause.getBlock())
        return

    @classmethod
    def visit_for_stmt(cls, _for_stmt=None):
        """
        Private method: Used to visit a single for-stmt, update its scope and create the corresponding sub-scope.
        :param _for_stmt: a for-statement.
        :type _for_stmt: ASTForStmt
        """
        from pynestml.modelprocessor.ASTForStmt import ASTForStmt
        assert (_for_stmt is not None and isinstance(_for_stmt, ASTForStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of for-statement provided (%s)!' % type(_for_stmt)
        _for_stmt.getFrom().updateScope(_for_stmt.getScope())
        cls.visit_expression(_for_stmt.getFrom())
        _for_stmt.getTo().updateScope(_for_stmt.getScope())
        cls.visit_expression(_for_stmt.getTo())
        _for_stmt.getBlock().updateScope(_for_stmt.getScope())
        cls.visit_block(_for_stmt.getBlock())
        return

    @classmethod
    def visit_while_stmt(cls, _while_stmt=None):
        """
        Private method: Used to visit a single while-stmt, update its scope and create the corresponding sub-scope.
        :param _while_stmt: a while-statement.
        :type _while_stmt: ASTWhileStmt
        """
        from pynestml.modelprocessor.ASTWhileStmt import ASTWhileStmt
        assert (_while_stmt is not None and isinstance(_while_stmt, ASTWhileStmt)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of while-statement provided (%s)!' % type(_while_stmt)
        _while_stmt.getCondition().updateScope(_while_stmt.getScope())
        cls.visit_expression(_while_stmt.getCondition())
        _while_stmt.getBlock().updateScope(_while_stmt.getScope())
        cls.visit_block(_while_stmt.getBlock())
        return

    @classmethod
    def visit_data_type(cls, _data_type=None):
        """
        Private method: Used to visit a single data-type and update its scope.
        :param _data_type: a data-type.
        :type _data_type: ASTDataType
        """
        from pynestml.modelprocessor.ASTDatatype import ASTDatatype
        assert (_data_type is not None and isinstance(_data_type, ASTDatatype)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of data-type provided (%s)!' % type(_data_type)
        if _data_type.isUnitType():
            _data_type.getUnitType().updateScope(_data_type.getScope())
            return cls.visit_unit_type(_data_type.getUnitType())
        # besides updating the scope no operations are required, since no type symbols are added to the scope.
        return

    @classmethod
    def visit_unit_type(cls, _unit_type=None):
        """
        Private method: Used to visit a single unit-type and update its scope.
        :param _unit_type: a unit type.
        :type _unit_type: ASTUnitType
        """
        from pynestml.modelprocessor.ASTUnitType import ASTUnitType
        assert (_unit_type is not None and isinstance(_unit_type, ASTUnitType)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of unit-typ provided (%s)!' % type(_unit_type)
        if _unit_type.isPowerExpression():
            _unit_type.getBase().updateScope(_unit_type.getScope())
            cls.visit_unit_type(_unit_type.getBase())
        elif _unit_type.isEncapsulated():
            _unit_type.getCompoundUnit().updateScope(_unit_type.getScope())
            cls.visit_unit_type(_unit_type.getCompoundUnit())
        elif _unit_type.isDiv() or _unit_type.isTimes():
            if isinstance(_unit_type.getLhs(), ASTUnitType):  # lhs can be a numeric Or a unit-type
                _unit_type.getLhs().updateScope(_unit_type.getScope())
                cls.visit_unit_type(_unit_type.getLhs())
            _unit_type.getRhs().updateScope(_unit_type.getScope())
            cls.visit_unit_type(_unit_type.getRhs())
        return

    @classmethod
    def visit_expression(cls, _expr=None):
        """
        Private method: Used to visit a single expression and update its scope.
        :param _expr: an expression.
        :type _expr: ASTExpression
        """
        from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
        from pynestml.modelprocessor.ASTExpression import ASTExpression
        from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
        from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
        from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
        if isinstance(_expr, ASTSimpleExpression):
            return cls.visit_simple_expression(_expr)
        assert (_expr is not None and isinstance(_expr, ASTExpression)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of expression provided (%s)!' % type(_expr)
        if _expr.isLogicalNot():
            _expr.getExpression().updateScope(_expr.getScope())
            cls.visit_expression(_expr.getExpression())
        elif _expr.isEncapsulated():
            _expr.getExpression().updateScope(_expr.getScope())
            cls.visit_expression(_expr.getExpression())
        elif _expr.isUnaryOperator():
            _expr.getUnaryOperator().updateScope(_expr.getScope())
            cls.visit_unary_operator(_expr.getUnaryOperator())
            _expr.getExpression().updateScope(_expr.getScope())
            cls.visit_expression(_expr.getExpression())
        elif _expr.isCompoundExpression():
            _expr.getLhs().updateScope(_expr.getScope())
            cls.visit_expression(_expr.getLhs())
            _expr.getBinaryOperator().updateScope(_expr.getScope())
            if isinstance(_expr.getBinaryOperator(), ASTBitOperator):
                cls.visit_bit_operator(_expr.getBinaryOperator())
            elif isinstance(_expr.getBinaryOperator(), ASTComparisonOperator):
                cls.visit_comparison_operator(_expr.getBinaryOperator())
            elif isinstance(_expr.getBinaryOperator(), ASTLogicalOperator):
                cls.visit_logical_operator(_expr.getBinaryOperator())
            else:
                cls.visit_arithmetic_operator(_expr.getBinaryOperator())
            _expr.getRhs().updateScope(_expr.getScope())
            cls.visit_expression(_expr.getRhs())
        if _expr.isTernaryOperator():
            _expr.getCondition().updateScope(_expr.getScope())
            cls.visit_expression(_expr.getCondition())
            _expr.getIfTrue().updateScope(_expr.getScope())
            cls.visit_expression(_expr.getIfTrue())
            _expr.getIfNot().updateScope(_expr.getScope())
            cls.visit_expression(_expr.getIfNot())
        return

    @classmethod
    def visit_simple_expression(cls, _expr=None):
        """
        Private method: Used to visit a single simple expression and update its scope.
        :param _expr: a simple expression.
        :type _expr: ASTSimpleExpression
        """
        from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
        assert (_expr is not None and isinstance(_expr, ASTSimpleExpression)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of simple expression provided (%s)!' % type(_expr)
        if _expr.isFunctionCall():
            _expr.getFunctionCall().updateScope(_expr.getScope())
            cls.visit_function_call(_expr.getFunctionCall())
        elif _expr.isVariable() or _expr.hasUnit():
            _expr.getVariable().updateScope(_expr.getScope())
            cls.visit_variable(_expr.getVariable())
        return

    @classmethod
    def visit_unary_operator(cls, _unary_op=None):
        """
        Private method: Used to visit a single unary operator and update its scope.
        :param _unary_op: a single unary operator.
        :type _unary_op: ASTUnaryOperator
        """
        from pynestml.modelprocessor.ASTUnaryOperator import ASTUnaryOperator
        assert (_unary_op is not None and isinstance(_unary_op, ASTUnaryOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of unary operator provided (%s)!' % type(_unary_op)
        return

    @classmethod
    def visit_bit_operator(cls, _bit_op=None):
        """
        Private method: Used to visit a single unary operator and update its scope.
        :param _bit_op: a single bit operator.
        :type _bit_op: ASTBitOperator
        """
        from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
        assert (_bit_op is not None and isinstance(_bit_op, ASTBitOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of bit operator provided (%s)!' % type(_bit_op)
        return

    @classmethod
    def visit_comparison_operator(cls, _comparison_op=None):
        """
        Private method: Used to visit a single comparison operator and update its scope.
        :param _comparison_op: a single comparison operator.
        :type _comparison_op: ASTComparisonOperator
        """
        from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
        assert (_comparison_op is not None and isinstance(_comparison_op, ASTComparisonOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of comparison operator provided (%s)!' % type(
                _comparison_op)
        return

    @classmethod
    def visit_logical_operator(cls, _logical_op=None):
        """
        Private method: Used to visit a single logical operator and update its scope.
        :param _logical_op: a single logical operator.
        :type _logical_op: ASTLogicalOperator
        """
        from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
        assert (_logical_op is not None and isinstance(_logical_op, ASTLogicalOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of logical operator provided (%s)!' % type(_logical_op)
        return

    @classmethod
    def visit_variable(cls, _variable=None):
        """
        Private method: Used to visit a single variable and update its scope.
        :param _variable: a single variable.
        :type _variable: ASTVariable
        """
        from pynestml.modelprocessor.ASTVariable import ASTVariable
        assert (_variable is not None and isinstance(_variable, ASTVariable)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of variable provided (%s)!' % type(_variable)
        return

    @classmethod
    def visit_ode_function(cls, _ode_function=None):
        """
        Private method: Used to visit a single ode-function, create the corresponding symbol and update the scope.
        :param _ode_function: a single ode-function.
        :type _ode_function: ASTOdeFunction
        """
        from pynestml.modelprocessor.ASTOdeFunction import ASTOdeFunction
        from pynestml.modelprocessor.ASTUnitTypeVisitor import ASTUnitTypeVisitor
        from pynestml.modelprocessor.VariableSymbol import BlockType, VariableType
        assert (_ode_function is not None and isinstance(_ode_function, ASTOdeFunction)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of ode-function provided (%s)!' % type(_ode_function)
        type_symbol = PredefinedTypes.getTypeIfExists(ASTUnitTypeVisitor.visitDatatype(_ode_function.getDataType()))
        symbol = VariableSymbol(_referenced_object=_ode_function, _scope=_ode_function.getScope(),
                                _name=_ode_function.getVariableName(),
                                _blockType=BlockType.EQUATION,
                                _declaringExpression=_ode_function.getExpression(),
                                _isPredefined=False, _isFunction=True,
                                _isRecordable=_ode_function.isRecordable(),
                                _typeSymbol=type_symbol,
                                _variableType=VariableType.VARIABLE)
        symbol.setComment(_ode_function.getComment())
        _ode_function.getScope().addSymbol(symbol)
        _ode_function.getDataType().updateScope(_ode_function.getScope())
        cls.visit_data_type(_ode_function.getDataType())
        _ode_function.getExpression().updateScope(_ode_function.getScope())
        cls.visit_expression(_ode_function.getExpression())
        return

    @classmethod
    def visit_ode_shape(cls, _ode_shape=None):
        """
        Private method: Used to visit a single ode-shape, create the corresponding symbol and update the scope.
        :param _ode_shape: a single ode-shape.
        :type _ode_shape: ASTOdeShape
        """
        from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
        from pynestml.modelprocessor.VariableSymbol import VariableSymbol, BlockType
        from pynestml.modelprocessor.Symbol import SymbolKind
        assert (_ode_shape is not None and isinstance(_ode_shape, ASTOdeShape)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of ode-shape provided (%s)!' % type(_ode_shape)
        if _ode_shape.getVariable().getDifferentialOrder() == 0 and \
                _ode_shape.getScope().resolveToSymbol(_ode_shape.getVariable().getCompleteName(),
                                                      SymbolKind.VARIABLE) is None:
            symbol = VariableSymbol(_referenced_object=_ode_shape, _scope=_ode_shape.getScope(),
                                    _name=_ode_shape.getVariable().getName(),
                                    _blockType=BlockType.EQUATION,
                                    _declaringExpression=_ode_shape.getExpression(),
                                    _isPredefined=False, _isFunction=False,
                                    _isRecordable=True,
                                    _typeSymbol=PredefinedTypes.getRealType(), _variableType=VariableType.SHAPE)
            symbol.setComment(_ode_shape.getComment())
            _ode_shape.getScope().addSymbol(symbol)
        _ode_shape.getVariable().updateScope(_ode_shape.getScope())
        cls.visit_variable(_ode_shape.getVariable())
        _ode_shape.getExpression().updateScope(_ode_shape.getScope())
        cls.visit_expression(_ode_shape.getExpression())
        return

    @classmethod
    def visit_ode_equation(cls, _equation=None):
        """
        Private method: Used to visit a single ode-equation and update the corresponding scope.
        :param _equation: a single ode-equation.
        :type _equation: ASTOdeEquation
        """
        from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
        assert (_equation is not None and isinstance(_equation, ASTOdeEquation)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of ode-equation provided (%s)!' % type(_equation)
        _equation.getLhs().updateScope(_equation.getScope())
        cls.visit_variable(_equation.getLhs())
        _equation.getRhs().updateScope(_equation.getScope())
        cls.visit_expression(_equation.getRhs())
        return

    @classmethod
    def visit_block_with_variables(cls, _block=None):
        """
        Private method: Used to visit a single block of variables and update its scope.
        :param _block: a block with declared variables.
        :type _block: ASTBlockWithVariables
        """
        from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
        from pynestml.modelprocessor.VariableSymbol import BlockType
        assert (_block is not None and isinstance(_block, ASTBlockWithVariables)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of block with variables provided (%s)!' % type(_block)
        cls.__currentBlockType = BlockType.STATE if _block.isState() else \
            BlockType.INTERNALS if _block.isInternals() else \
            BlockType.PARAMETERS if _block.isParameters() else \
            BlockType.INITIAL_VALUES
        for decl in _block.getDeclarations():
            decl.updateScope(_block.getScope())
            cls.visit_declaration(decl)
        cls.__currentBlockType = None
        return

    @classmethod
    def visit_equations_block(cls, _block=None):
        """
        Private method: Used to visit a single equations block and update its scope.
        :param _block: a single equations block.
        :type _block: ASTEquationsBlock
        """
        from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
        from pynestml.modelprocessor.ASTOdeFunction import ASTOdeFunction
        from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
        assert (_block is not None and isinstance(_block, ASTEquationsBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of equations block provided (%s)!' % type(_block)
        for decl in _block.getDeclarations():
            decl.updateScope(_block.getScope())
            if isinstance(decl, ASTOdeFunction):
                cls.visit_ode_function(decl)
            elif isinstance(decl, ASTOdeShape):
                cls.visit_ode_shape(decl)
            else:
                cls.visit_ode_equation(decl)
        return

    @classmethod
    def visit_input_block(cls, _block=None):
        """
        Private method: Used to visit a single input block and update its scope.
        :param _block: a single input block.
        :type _block: ASTInputBlock
        """
        from pynestml.modelprocessor.ASTInputBlock import ASTInputBlock
        assert (_block is not None and isinstance(_block, ASTInputBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of input-block provided (%s)!' % type(_block)
        for line in _block.getInputLines():
            line.updateScope(_block.getScope())
            cls.visit_input_line(line)
        return

    @classmethod
    def visit_output_block(cls, _block=None):
        """
        Private method: Used to visit a single output block and visit its scope.
        :param _block: a single output block.
        :type _block: ASTOutputBlock
        """
        from pynestml.modelprocessor.ASTOutputBlock import ASTOutputBlock
        assert (_block is not None and isinstance(_block, ASTOutputBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of output-block provided (%s)!' % type(_block)
        return

    @classmethod
    def visit_input_line(cls, _line=None):
        """
        Private method: Used to visit a single input line, create the corresponding symbol and update the scope.
        :param _line: a single input line.
        :type _line: ASTInputLine
        """
        from pynestml.modelprocessor.ASTInputLine import ASTInputLine
        from pynestml.modelprocessor.VariableSymbol import BlockType, VariableType
        assert (_line is not None and isinstance(_line, ASTInputLine)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of input-line provided (%s)!' % type(_line)
        from pynestml.modelprocessor.VariableSymbol import VariableSymbol
        buffer_type = BlockType.INPUT_BUFFER_SPIKE if _line.isSpike() else BlockType.INPUT_BUFFER_CURRENT
        if _line.isSpike() and _line.hasDatatype():
            _line.getDatatype().updateScope(_line.getScope())
            cls.visit_data_type(_line.getDatatype())
            type_symbol = _line.getDatatype().getTypeSymbol()
        elif _line.isSpike():
            code, message = Messages.getBufferTypeNotDefined(_line.getName())
            Logger.logMessage(_code=code, _message=message, _errorPosition=_line.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.WARNING)
            type_symbol = PredefinedTypes.getTypeIfExists('nS')
        else:
            type_symbol = PredefinedTypes.getTypeIfExists('pA')
        type_symbol.is_buffer = True  # set it as a buffer
        symbol = VariableSymbol(_referenced_object=_line, _scope=_line.getScope(), _name=_line.getName(),
                                _blockType=buffer_type, _vectorParameter=_line.getIndexParameter(),
                                _isPredefined=False, _isFunction=False, _isRecordable=False,
                                _typeSymbol=type_symbol, _variableType=VariableType.BUFFER)
        symbol.setComment(_line.getComment())
        _line.getScope().addSymbol(symbol)
        for inputType in _line.getInputTypes():
            cls.visit_input_type(inputType)
            inputType.updateScope(_line.getScope())
        return

    @classmethod
    def visit_input_type(cls, _type=None):
        """
        Private method: Used to visit a single input type and update its scope.
        :param _type: a single input-type.
        :type _type: ASTInputType
        """
        from pynestml.modelprocessor.ASTInputType import ASTInputType
        assert (_type is not None and isinstance(_type, ASTInputType)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of input-type provided (%s)!' % type(_type)
        return

    @classmethod
    def visit_arithmetic_operator(cls, _arithmetic_op=None):
        """
        Private method: Used to visit a single arithmetic operator and update its scope.
        :param _arithmetic_op: a single arithmetic operator.
        :type _arithmetic_op: ASTArithmeticOperator
        """
        from pynestml.modelprocessor.ASTArithmeticOperator import ASTArithmeticOperator
        assert (_arithmetic_op is not None and isinstance(_arithmetic_op, ASTArithmeticOperator)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of arithmetic operator provided (%s)!' % type(
                _arithmetic_op)
        return

    @classmethod
    def make_implicit_odes_explicit(cls, _equations_block=None):
        """
        This method inspects a handed over block of equations and makes all implicit declarations of odes explicit.
        E.g. the declaration g_in'' implies that there have to be, either implicit or explicit, g_in' and g_in
        stated somewhere. This method collects all non explicitly defined elements and adds them to the model.
        :param _equations_block: a single equations block
        :type _equations_block: ASTEquationsBlock
        """
        from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
        from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
        from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
        from pynestml.modelprocessor.ASTVariable import ASTVariable
        from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
        from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
        assert (_equations_block is not None and isinstance(_equations_block, ASTEquationsBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of equations block provided (%s)!' % type(_equations_block)
        checked = list()  # used to avoid redundant checking
        for declaration in _equations_block.getDeclarations():
            if declaration in checked:
                continue
            if isinstance(declaration, ASTOdeShape) and declaration.getVariable().getDifferentialOrder() > 0:
                # now we found a variable with order > 0, thus check if all previous orders have been defined
                order = declaration.getVariable().getDifferentialOrder()
                # check for each smaller order if it is defined
                for i in range(1, order):
                    found = False
                    for shape in _equations_block.getOdeShapes():
                        if shape.getVariable().getName() == declaration.getVariable().getName() and \
                                shape.getVariable().getDifferentialOrder() == i:
                            found = True
                            break
                    # now if we did not found the corresponding declaration, we have to add it by hand
                    if not found:
                        lhs_variable = ASTVariable.makeASTVariable(_name=declaration.getVariable().getName(),
                                                                   _differentialOrder=i,
                                                                   _sourcePosition=ASTSourcePosition.
                                                                   getAddedSourcePosition())
                        rhs_variable = ASTVariable.makeASTVariable(_name=declaration.getVariable().getName(),
                                                                   _differentialOrder=i,
                                                                   _sourcePosition=ASTSourcePosition.
                                                                   getAddedSourcePosition())
                        expression = ASTSimpleExpression.makeASTSimpleExpression(_variable=rhs_variable,
                                                                                 _sourcePosition=ASTSourcePosition.
                                                                                 getAddedSourcePosition())
                        _equations_block.getDeclarations().append(
                            ASTOdeShape.makeASTOdeShape(_lhs=lhs_variable,
                                                        _rhs=expression,
                                                        _sourcePosition=ASTSourcePosition.getAddedSourcePosition()))
            if isinstance(declaration, ASTOdeEquation):
                # now we found a variable with order > 0, thus check if all previous orders have been defined
                order = declaration.getLhs().getDifferentialOrder()
                # check for each smaller order if it is defined
                for i in range(1, order):
                    found = False
                    for ode in _equations_block.getOdeEquations():
                        if ode.getLhs().getName() == declaration.getLhs().getName() and \
                                ode.getLhs().getDifferentialOrder() == i:
                            found = True
                            break
                    # now if we did not found the corresponding declaration, we have to add it by hand
                    if not found:
                        lhs_variable = ASTVariable.makeASTVariable(_name=declaration.getLhs().getName(),
                                                                   _differentialOrder=i,
                                                                   _sourcePosition=ASTSourcePosition.
                                                                   getAddedSourcePosition())
                        rhs_variable = ASTVariable.makeASTVariable(_name=declaration.getLhs().getName(),
                                                                   _differentialOrder=i,
                                                                   _sourcePosition=ASTSourcePosition.
                                                                   getAddedSourcePosition())
                        expression = ASTSimpleExpression.makeASTSimpleExpression(_variable=rhs_variable,
                                                                                 _sourcePosition=ASTSourcePosition.
                                                                                 getAddedSourcePosition())
                        _equations_block.getDeclarations().append(
                            ASTOdeEquation.makeASTOdeEquation(_lhs=lhs_variable,
                                                              _rhs=expression,
                                                              _sourcePosition=ASTSourcePosition
                                                              .getAddedSourcePosition()))
            checked.append(declaration)

    @classmethod
    def mark_conductance_based_buffers(cls, _input_lines):
        from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
        from pynestml.modelprocessor.Symbol import SymbolKind
        # this is the updated version, where nS buffers are marked as conductance based
        for bufferDeclaration in _input_lines:
            if bufferDeclaration.isSpike():
                symbol = bufferDeclaration.getScope().resolveToSymbol(bufferDeclaration.getName(), SymbolKind.VARIABLE)
                if symbol is not None and symbol.getTypeSymbol().equals(PredefinedTypes.getTypeIfExists('nS')):
                    symbol.setConductanceBased(True)
        return

    @classmethod
    def assign_ode_to_variables(cls, _ode_block=None):
        """
        Adds for each variable symbol the corresponding ode declaration if present.
        :param _ode_block: a single block of ode declarations.
        :type _ode_block: ASTEquations
        """
        from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
        from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
        from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
        assert (_ode_block is not None and isinstance(_ode_block, ASTEquationsBlock)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of equations block provided (%s)!' % type(_ode_block)
        for decl in _ode_block.getDeclarations():
            if isinstance(decl, ASTOdeEquation):
                cls.add_ode_to_variable(decl)
            if isinstance(decl, ASTOdeShape):
                cls.add_ode_shape_to_variable(decl)
        return

    @classmethod
    def add_ode_to_variable(cls, _ode_equation=None):
        """
        Resolves to the corresponding symbol and updates the corresponding ode-declaration. In the case that
        :param _ode_equation: a single ode-equation
        :type _ode_equation: ASTOdeEquation
        """
        from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
        from pynestml.modelprocessor.Symbol import SymbolKind
        assert (_ode_equation is not None and isinstance(_ode_equation, ASTOdeEquation)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of equation provided (%s)!' % type(_ode_equation)
        # the definition of a differential equations is defined by stating the derivation, thus derive the actual order
        diff_order = _ode_equation.getLhs().getDifferentialOrder() - 1
        # we check if the corresponding symbol already exists, e.g. V_m' has already been declared
        existing_symbol = _ode_equation.getScope().resolveToSymbol(_ode_equation.getLhs().getName() + '\'' * diff_order,
                                                                   SymbolKind.VARIABLE)
        if existing_symbol is not None:
            existing_symbol.setOdeDefinition(_ode_equation.getRhs())
            _ode_equation.getScope().updateVariableSymbol(existing_symbol)
            code, message = Messages.getOdeUpdated(_ode_equation.getLhs().getNameOfLhs())
            Logger.logMessage(_errorPosition=existing_symbol.referenced_object.getSourcePosition(),
                              _code=code, _message=message, _logLevel=LOGGING_LEVEL.INFO)
        else:
            code, message = Messages.getNoVariableFound(_ode_equation.getLhs().getNameOfLhs())
            Logger.logMessage(_code=code, _message=message, _errorPosition=_ode_equation.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return

    @classmethod
    def add_ode_shape_to_variable(cls, _ode_shape=None):
        """
        Adds the shape as the defining equation.
        :param _ode_shape: a single shape object.
        :type _ode_shape: ASTOdeShape
        """
        from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
        from pynestml.modelprocessor.Symbol import SymbolKind
        from pynestml.modelprocessor.VariableSymbol import VariableType
        assert (_ode_shape is not None and isinstance(_ode_shape, ASTOdeShape)), \
            '(PyNestML.SymbolTable.Visitor) No or wrong type of shape provided (%s)!' % type(_ode_shape)
        if _ode_shape.getVariable().getDifferentialOrder() == 0:
            # we only update those which define an ode
            return
        # we check if the corresponding symbol already exists, e.g. V_m' has already been declared
        existing_symbol = _ode_shape.getScope().resolveToSymbol(_ode_shape.getVariable().getNameOfLhs(),
                                                                SymbolKind.VARIABLE)
        if existing_symbol is not None:
            existing_symbol.setOdeDefinition(_ode_shape.getExpression())
            existing_symbol.setVariableType(VariableType.SHAPE)
            _ode_shape.getScope().updateVariableSymbol(existing_symbol)
            code, message = Messages.getOdeUpdated(_ode_shape.getVariable().getNameOfLhs())
            Logger.logMessage(_errorPosition=existing_symbol.referenced_object.getSourcePosition(),
                              _code=code, _message=message, _logLevel=LOGGING_LEVEL.INFO)
        else:
            code, message = Messages.getNoVariableFound(_ode_shape.getVariable().getNameOfLhs())
            Logger.logMessage(_code=code, _message=message, _errorPosition=_ode_shape.getSourcePosition(),
                              _logLevel=LOGGING_LEVEL.ERROR)
        return
