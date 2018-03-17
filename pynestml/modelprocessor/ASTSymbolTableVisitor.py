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
from typing import Generator, List

from pynestml.modelprocessor.ASTAssignment import ASTAssignment
from pynestml.modelprocessor.ASTBlock import ASTBlock
from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
from pynestml.modelprocessor.ASTBody import ASTBody
from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
from pynestml.modelprocessor.ASTDatatype import ASTDatatype
from pynestml.modelprocessor.ASTDeclaration import ASTDeclaration
from pynestml.modelprocessor.ASTElifClause import ASTElifClause
from pynestml.modelprocessor.ASTElseClause import ASTElseClause
from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
from pynestml.modelprocessor.ASTForStmt import ASTForStmt
from pynestml.modelprocessor.ASTFunction import ASTFunction
from pynestml.modelprocessor.ASTFunctionCall import ASTFunctionCall
from pynestml.modelprocessor.ASTIfClause import ASTIfClause
from pynestml.modelprocessor.ASTIfStmt import ASTIfStmt
from pynestml.modelprocessor.ASTInputBlock import ASTInputBlock
from pynestml.modelprocessor.ASTInputLine import ASTInputLine
from pynestml.modelprocessor.ASTNeuron import ASTNeuron
from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
from pynestml.modelprocessor.ASTOdeFunction import ASTOdeFunction
from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
from pynestml.modelprocessor.ASTOutputBlock import ASTOutputBlock
from pynestml.modelprocessor.ASTReturnStmt import ASTReturnStmt
from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
from pynestml.modelprocessor.ASTUnitType import ASTUnitType
from pynestml.modelprocessor.ASTUpdateBlock import ASTUpdateBlock
from pynestml.modelprocessor.ASTWhileStmt import ASTWhileStmt
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
        __current_block_type This variable is used to store information regarding which block with declarations is
                            currently visited. It is used to update the BlockType of variable symbols to the correct
                            element.
    """
    __current_block_type = None  # type: BlockType

    @classmethod
    def update_symbol_table(cls, _ast_neuron):
        # type: (ASTNeuron) -> None
        Logger.setCurrentNeuron(_ast_neuron)
        code, message = Messages.getStartBuildingSymbolTable()
        Logger.logMessage(_neuron=_ast_neuron, _code=code, _errorPosition=_ast_neuron.getSourcePosition(),
                          _message=message, _logLevel=LOGGING_LEVEL.INFO)
        symbol_table_visitor = ASTSymbolTableVisitor()
        symbol_table_visitor.visit_neuron(_ast_neuron)
        Logger.setCurrentNeuron(None)
        return

    def visit_neuron(self, _neuron):
        # type: (ASTNeuron) -> None
        # before starting the work on the neuron, make everything which was implicit explicit
        # but if we have a model without an equations block, just skip this step
        if _neuron.getEquationsBlocks() is not None:
            self.make_implicit_odes_explicit(_neuron.getEquationsBlocks())
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
        self.visit_body(_neuron.getBody())
        # before following checks occur, we need to ensure several simple properties
        CoCosManager.postSymbolTableBuilderChecks(_neuron)
        # the following part is done in order to mark conductance based buffers as such.
        if _neuron.getInputBlocks() is not None and _neuron.getEquationsBlocks() is not None and \
                len(_neuron.getEquationsBlocks().getDeclarations()) > 0:
            # this case should be prevented, since several input blocks result in  a incorrect model
            buffers = (buf for buf in _neuron.getInputBlocks().getInputLines())

            self.mark_conductance_based_buffers(buffers)
        # now update the equations
        if _neuron.getEquationsBlocks() is not None and len(_neuron.getEquationsBlocks().getDeclarations()) > 0:
            equation_block = _neuron.getEquationsBlocks()
            self.assign_ode_to_variables(equation_block)
        CoCosManager.postOdeSpecificationChecks(_neuron)
        return

    def visit_body(self, _body):
        # type: (ASTBody) -> None
        from pynestml.modelprocessor.ASTBlockWithVariables import ASTBlockWithVariables
        from pynestml.modelprocessor.ASTUpdateBlock import ASTUpdateBlock
        from pynestml.modelprocessor.ASTEquationsBlock import ASTEquationsBlock
        from pynestml.modelprocessor.ASTInputBlock import ASTInputBlock
        from pynestml.modelprocessor.ASTOutputBlock import ASTOutputBlock
        from pynestml.modelprocessor.ASTFunction import ASTFunction
        for bodyElement in _body.getBodyElements():
            bodyElement.updateScope(_body.getScope())
            if isinstance(bodyElement, ASTBlockWithVariables):
                self.visit_block_with_variables(bodyElement)
            elif isinstance(bodyElement, ASTUpdateBlock):
                self.visit_update_block(bodyElement)
            elif isinstance(bodyElement, ASTEquationsBlock):
                self.visit_equations_block(bodyElement)
            elif isinstance(bodyElement, ASTInputBlock):
                self.visit_input_block(bodyElement)
            elif isinstance(bodyElement, ASTOutputBlock):
                self.visit_output_block(bodyElement)
            elif isinstance(bodyElement, ASTFunction):
                self.visit_function_block(bodyElement)
        return

    def visit_function_block(self, _block):
        # type: (ASTFunction) -> None
        from pynestml.modelprocessor.ASTUnitTypeVisitor import ASTUnitTypeVisitor
        self.__current_block_type = BlockType.LOCAL  # before entering, update the current block type
        symbol = FunctionSymbol(_scope=_block.getScope(), _referenced_object=_block, _paramTypes=list(),
                                _name=_block.getName())
        symbol.setComment(_block.getComment())
        _block.getScope().addSymbol(symbol)
        scope = Scope(_scopeType=ScopeType.FUNCTION, _enclosingScope=_block.getScope(),
                      _sourcePosition=_block.getSourcePosition())
        _block.getScope().addScope(scope)
        for arg in _block.getParameters():
            # first visit the data type to ensure that variable symbol can receive a combined data type
            arg.getDataType().updateScope(scope)
            self.visit_data_type(arg.getDataType())
            # given the fact that the name is not directly equivalent to the one as stated in the model,
            # we have to get it by the sub-visitor
            type_name = ASTUnitTypeVisitor.visitDatatype(arg.getDataType())
            # first collect the types for the parameters of the function symbol
            symbol.addParameterType(PredefinedTypes.getTypeIfExists(type_name))
            # update the scope of the arg
            arg.updateScope(scope)
            # create the corresponding variable symbol representing the parameter
            var_symbol = VariableSymbol(_referenced_object=arg, _scope=scope, _name=arg.getName(),
                                        _blockType=BlockType.LOCAL,
                                        _typeSymbol=PredefinedTypes.getTypeIfExists(type_name),
                                        _variableType=VariableType.VARIABLE)
            scope.addSymbol(var_symbol)
        if _block.hasReturnType():
            _block.get_return_data_type().updateScope(scope)
            self.visit_data_type(_block.get_return_data_type())
            symbol.setReturnType(
                PredefinedTypes.getTypeIfExists(ASTUnitTypeVisitor.visitDatatype(_block.get_return_data_type())))
        else:
            symbol.setReturnType(PredefinedTypes.getVoidType())
        _block.getBlock().updateScope(scope)
        self.visit_block(_block.getBlock())
        self.__current_block_type = None  # before leaving update the type
        return

    def visit_update_block(self, _block):
        # type: (ASTUpdateBlock) -> None
        self.__current_block_type = BlockType.LOCAL
        scope = Scope(_scopeType=ScopeType.UPDATE, _enclosingScope=_block.getScope(),
                      _sourcePosition=_block.getSourcePosition())
        _block.getScope().addScope(scope)
        _block.getBlock().updateScope(scope)
        self.visit_block(_block.getBlock())
        self.__current_block_type = BlockType.LOCAL
        return

    def visit_block(self, _block):
        # type: (ASTBlock) -> None
        from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
        from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
        for stmt in _block.getStmts():
            if isinstance(stmt, ASTSmallStmt):
                stmt.updateScope(_block.getScope())
                self.visit_small_stmt(stmt)
            elif isinstance(stmt, ASTCompoundStmt):
                stmt.updateScope(_block.getScope())
                self.visit_compound_stmt(stmt)
        return

    def visit_small_stmt(self, _stmt):
        # type: (ASTSmallStmt) -> None
        if _stmt.isDeclaration():
            _stmt.getDeclaration().updateScope(_stmt.getScope())
            self.visit_declaration(_stmt.getDeclaration())
        elif _stmt.isAssignment():
            _stmt.getAssignment().updateScope(_stmt.getScope())
            self.visit_assignment(_stmt.getAssignment())
        elif _stmt.isFunctionCall():
            _stmt.getFunctionCall().updateScope(_stmt.getScope())
            self.visit_function_call(_stmt.getFunctionCall())
        elif _stmt.isReturnStmt():
            _stmt.getReturnStmt().updateScope(_stmt.getScope())
            self.visit_return_stmt(_stmt.getReturnStmt())
        return

    def visit_compound_stmt(self, _stmt):
        # type: (ASTCompoundStmt) -> None
        if _stmt.isIfStmt():
            _stmt.getIfStmt().updateScope(_stmt.getScope())
            self.visit_if_stmt(_stmt.getIfStmt())
        elif _stmt.isWhileStmt():
            _stmt.getWhileStmt().updateScope(_stmt.getScope())
            self.visit_while_stmt(_stmt.getWhileStmt())
        else:
            _stmt.getForStmt().updateScope(_stmt.getScope())
            self.visit_for_stmt(_stmt.getForStmt())
        return

    def visit_assignment(self, _assignment):
        # type: (ASTAssignment) -> None
        _assignment.getVariable().updateScope(_assignment.getScope())
        self.visit_variable(_assignment.getVariable())
        _assignment.getExpression().updateScope(_assignment.getScope())
        self.visit_expression(_assignment.getExpression())
        return

    def visit_function_call(self, _function_call):
        # type: (ASTFunctionCall) -> None
        for arg in _function_call.getArgs():
            arg.updateScope(_function_call.getScope())
            self.visit_expression(arg)
        return

    def visit_declaration(self, _declaration):
        # type: (ASTDeclaration) -> None
        from pynestml.modelprocessor.VariableSymbol import VariableSymbol, BlockType, VariableType
        from pynestml.modelprocessor.ASTUnitTypeVisitor import ASTUnitTypeVisitor
        expression = _declaration.getExpression() if _declaration.hasExpression() else None
        type_name = ASTUnitTypeVisitor.visitDatatype(_declaration.getDataType())
        # all declarations in the state block are recordable
        is_recordable = (_declaration.isRecordable() or
                         self.__current_block_type == BlockType.STATE or
                         self.__current_block_type == BlockType.INITIAL_VALUES)
        init_value = _declaration.getExpression() if self.__current_block_type == BlockType.INITIAL_VALUES else None
        vector_parameter = _declaration.getSizeParameter()
        for var in _declaration.getVariables():  # for all variables declared create a new symbol
            var.updateScope(_declaration.getScope())
            type_symbol = PredefinedTypes.getTypeIfExists(type_name)
            symbol = VariableSymbol(_referenced_object=_declaration, _scope=_declaration.getScope(),
                                    _name=var.getCompleteName(), _blockType=self.__current_block_type,
                                    _declaringExpression=expression, _isFunction=_declaration.isFunction(),
                                    _isRecordable=is_recordable, _typeSymbol=type_symbol, _initialValue=init_value,
                                    _vectorParameter=vector_parameter, _variableType=VariableType.VARIABLE)
            symbol.setComment(_declaration.getComment())
            _declaration.getScope().addSymbol(symbol)
            var.setTypeSymbol(Either.value(type_symbol))
            self.visit_variable(var)
        _declaration.getDataType().updateScope(_declaration.getScope())
        self.visit_data_type(_declaration.getDataType())
        if _declaration.hasExpression():
            _declaration.getExpression().updateScope(_declaration.getScope())
            self.visit_expression(_declaration.getExpression())
        if _declaration.hasInvariant():
            _declaration.getInvariant().updateScope(_declaration.getScope())
            self.visit_expression(_declaration.getInvariant())
        return

    def visit_return_stmt(self, _return_stmt):
        # type: (ASTReturnStmt) -> None
        if _return_stmt.hasExpression():
            _return_stmt.getExpression().updateScope(_return_stmt.getScope())
            self.visit_expression(_return_stmt.getExpression())
        return

    def visit_if_stmt(self, _if_stmt):
        # type: (ASTIfStmt) -> None
        _if_stmt.getIfClause().updateScope(_if_stmt.getScope())
        self.visit_if_clause(_if_stmt.getIfClause())
        for elIf in _if_stmt.getElifClauses():
            elIf.updateScope(_if_stmt.getScope())
            self.visit_elif_clause(elIf)
        if _if_stmt.hasElseClause():
            _if_stmt.getElseClause().updateScope(_if_stmt.getScope())
            self.visit_else_clause(_if_stmt.getElseClause())
        return

    def visit_if_clause(self, _if_clause):
        # type: (ASTIfClause) -> None
        _if_clause.getCondition().updateScope(_if_clause.getScope())
        self.visit_expression(_if_clause.getCondition())
        _if_clause.getBlock().updateScope(_if_clause.getScope())
        self.visit_block(_if_clause.getBlock())
        return

    def visit_elif_clause(self, _elif_clause):
        # type: (ASTElifClause) -> None
        _elif_clause.getCondition().updateScope(_elif_clause.getScope())
        self.visit_expression(_elif_clause.getCondition())
        _elif_clause.getBlock().updateScope(_elif_clause.getScope())
        self.visit_block(_elif_clause.getBlock())
        return

    def visit_else_clause(self, _else_clause):
        # type: (ASTElseClause) -> None
        _else_clause.getBlock().updateScope(_else_clause.getScope())
        self.visit_block(_else_clause.getBlock())
        return

    def visit_for_stmt(self, _for_stmt):
        # type: (ASTForStmt) -> None
        _for_stmt.getFrom().updateScope(_for_stmt.getScope())
        self.visit_expression(_for_stmt.getFrom())
        _for_stmt.getTo().updateScope(_for_stmt.getScope())
        self.visit_expression(_for_stmt.getTo())
        _for_stmt.getBlock().updateScope(_for_stmt.getScope())
        self.visit_block(_for_stmt.getBlock())
        return

    def visit_while_stmt(self, _while_stmt):
        # type: (ASTWhileStmt) -> None
        _while_stmt.getCondition().updateScope(_while_stmt.getScope())
        self.visit_expression(_while_stmt.getCondition())
        _while_stmt.getBlock().updateScope(_while_stmt.getScope())
        self.visit_block(_while_stmt.getBlock())
        return

    def visit_data_type(self, _data_type):
        # type: (ASTDatatype) -> None
        if _data_type.isUnitType():
            _data_type.getUnitType().updateScope(_data_type.getScope())
            return self.visit_unit_type(_data_type.getUnitType())
        # besides updating the scope no operations are required, since no type symbols are added to the scope.
        return

    def visit_unit_type(self, _unit_type):
        # type: (ASTUnitType) -> None
        if _unit_type.isPowerExpression():
            _unit_type.getBase().updateScope(_unit_type.getScope())
            self.visit_unit_type(_unit_type.getBase())
        elif _unit_type.isEncapsulated():
            _unit_type.getCompoundUnit().updateScope(_unit_type.getScope())
            self.visit_unit_type(_unit_type.getCompoundUnit())
        elif _unit_type.isDiv() or _unit_type.isTimes():
            if isinstance(_unit_type.getLhs(), ASTUnitType):  # lhs can be a numeric Or a unit-type
                _unit_type.getLhs().updateScope(_unit_type.getScope())
                self.visit_unit_type(_unit_type.getLhs())
            _unit_type.getRhs().updateScope(_unit_type.getScope())
            self.visit_unit_type(_unit_type.getRhs())
        return

    def visit_expression(self, _expr):
        # type: (ASTExpression) -> None
        from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
        from pynestml.modelprocessor.ASTExpression import ASTExpression
        from pynestml.modelprocessor.ASTBitOperator import ASTBitOperator
        from pynestml.modelprocessor.ASTLogicalOperator import ASTLogicalOperator
        from pynestml.modelprocessor.ASTComparisonOperator import ASTComparisonOperator
        if isinstance(_expr, ASTSimpleExpression):
            return self.visit_simple_expression(_expr)
        if _expr.isLogicalNot():
            _expr.getExpression().updateScope(_expr.getScope())
            self.visit_expression(_expr.getExpression())
        elif _expr.isEncapsulated():
            _expr.getExpression().updateScope(_expr.getScope())
            self.visit_expression(_expr.getExpression())
        elif _expr.isUnaryOperator():
            _expr.getUnaryOperator().updateScope(_expr.getScope())
            self.visit_unary_operator(_expr.getUnaryOperator())
            _expr.getExpression().updateScope(_expr.getScope())
            self.visit_expression(_expr.getExpression())
        elif _expr.isCompoundExpression():
            _expr.getLhs().updateScope(_expr.getScope())
            self.visit_expression(_expr.getLhs())
            _expr.getBinaryOperator().updateScope(_expr.getScope())
            if isinstance(_expr.getBinaryOperator(), ASTBitOperator):
                self.visit_bit_operator(_expr.getBinaryOperator())
            elif isinstance(_expr.getBinaryOperator(), ASTComparisonOperator):
                self.visit_comparison_operator(_expr.getBinaryOperator())
            elif isinstance(_expr.getBinaryOperator(), ASTLogicalOperator):
                self.visit_logical_operator(_expr.getBinaryOperator())
            else:
                self.visit_arithmetic_operator(_expr.getBinaryOperator())
            _expr.getRhs().updateScope(_expr.getScope())
            self.visit_expression(_expr.getRhs())
        if _expr.isTernaryOperator():
            _expr.getCondition().updateScope(_expr.getScope())
            self.visit_expression(_expr.getCondition())
            _expr.getIfTrue().updateScope(_expr.getScope())
            self.visit_expression(_expr.getIfTrue())
            _expr.getIfNot().updateScope(_expr.getScope())
            self.visit_expression(_expr.getIfNot())
        return

    def visit_simple_expression(self, _expr):
        # type: (ASTSimpleExpression) -> None
        if _expr.isFunctionCall():
            _expr.getFunctionCall().updateScope(_expr.getScope())
            self.visit_function_call(_expr.getFunctionCall())
        elif _expr.isVariable() or _expr.hasUnit():
            _expr.getVariable().updateScope(_expr.getScope())
            self.visit_variable(_expr.getVariable())
        return

    def visit_ode_function(self, _ode_function):
        # type: (ASTOdeFunction) -> None
        from pynestml.modelprocessor.ASTUnitTypeVisitor import ASTUnitTypeVisitor
        from pynestml.modelprocessor.VariableSymbol import BlockType, VariableType
        type_symbol = PredefinedTypes.getTypeIfExists(ASTUnitTypeVisitor.visitDatatype(_ode_function.getDataType()))
        symbol = VariableSymbol(_referenced_object=_ode_function, _scope=_ode_function.getScope(),
                                _name=_ode_function.getVariableName(), _blockType=BlockType.EQUATION,
                                _declaringExpression=_ode_function.getExpression(), _isFunction=True,
                                _isRecordable=_ode_function.isRecordable(), _typeSymbol=type_symbol,
                                _variableType=VariableType.VARIABLE)
        symbol.setComment(_ode_function.getComment())
        _ode_function.getScope().addSymbol(symbol)
        _ode_function.getDataType().updateScope(_ode_function.getScope())
        self.visit_data_type(_ode_function.getDataType())
        _ode_function.getExpression().updateScope(_ode_function.getScope())
        self.visit_expression(_ode_function.getExpression())
        return

    def visit_ode_shape(self, _ode_shape):
        # type: (ASTOdeShape) -> None
        from pynestml.modelprocessor.VariableSymbol import VariableSymbol, BlockType
        from pynestml.modelprocessor.Symbol import SymbolKind
        if _ode_shape.getVariable().getDifferentialOrder() == 0 and \
                _ode_shape.getScope().resolveToSymbol(_ode_shape.getVariable().getCompleteName(),
                                                      SymbolKind.VARIABLE) is None:
            symbol = VariableSymbol(_referenced_object=_ode_shape, _scope=_ode_shape.getScope(),
                                    _name=_ode_shape.getVariable().getName(), _blockType=BlockType.EQUATION,
                                    _declaringExpression=_ode_shape.getExpression(), _isRecordable=True,
                                    _typeSymbol=PredefinedTypes.getRealType(), _variableType=VariableType.SHAPE)
            symbol.setComment(_ode_shape.getComment())
            _ode_shape.getScope().addSymbol(symbol)
        _ode_shape.getVariable().updateScope(_ode_shape.getScope())
        self.visit_variable(_ode_shape.getVariable())
        _ode_shape.getExpression().updateScope(_ode_shape.getScope())
        self.visit_expression(_ode_shape.getExpression())
        return

    def visit_ode_equation(self, _equation):
        # type: (ASTOdeEquation) -> None
        _equation.getLhs().updateScope(_equation.getScope())
        self.visit_variable(_equation.getLhs())
        _equation.getRhs().updateScope(_equation.getScope())
        self.visit_expression(_equation.getRhs())
        return

    def visit_block_with_variables(self, _block):
        # type: (ASTBlockWithVariables) -> None
        from pynestml.modelprocessor.VariableSymbol import BlockType
        self.__current_block_type = (BlockType.STATE if _block.isState() else
                                     BlockType.INTERNALS if _block.isInternals() else
                                     BlockType.PARAMETERS if _block.isParameters() else
                                     BlockType.INITIAL_VALUES)
        for decl in _block.getDeclarations():
            decl.updateScope(_block.getScope())
            self.visit_declaration(decl)
        self.__current_block_type = None
        return

    def visit_equations_block(self, _block):
        # type: (ASTEquationsBlock) -> None
        from pynestml.modelprocessor.ASTOdeFunction import ASTOdeFunction
        from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
        for decl in _block.getDeclarations():
            decl.updateScope(_block.getScope())
            if isinstance(decl, ASTOdeFunction):
                self.visit_ode_function(decl)
            elif isinstance(decl, ASTOdeShape):
                self.visit_ode_shape(decl)
            else:
                self.visit_ode_equation(decl)
        return

    def visit_input_block(self, _block):
        # type: (ASTInputBlock) -> None
        for line in _block.getInputLines():
            line.updateScope(_block.getScope())
            self.visit_input_line(line)
        return

    def visit_output_block(self, _block):
        # type: (ASTOutputBlock) -> None
        return

    def visit_input_line(self, _line):
        # type: (ASTInputLine) -> None
        from pynestml.modelprocessor.VariableSymbol import BlockType, VariableType
        from pynestml.modelprocessor.VariableSymbol import VariableSymbol
        buffer_type = BlockType.INPUT_BUFFER_SPIKE if _line.isSpike() else BlockType.INPUT_BUFFER_CURRENT
        if _line.isSpike() and _line.hasDatatype():
            _line.getDatatype().updateScope(_line.getScope())
            self.visit_data_type(_line.getDatatype())
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
                                _typeSymbol=type_symbol, _variableType=VariableType.BUFFER)
        symbol.setComment(_line.getComment())
        _line.getScope().addSymbol(symbol)
        for inputType in _line.getInputTypes():
            self.visit_input_type(inputType)
            inputType.updateScope(_line.getScope())
        return

    @staticmethod
    def make_implicit_odes_explicit(_equations_block):
        # type: (ASTEquationsBlock) -> None
        """
        This method inspects a handed over block of equations and makes all implicit declarations of odes explicit.
        E.g. the declaration g_in'' implies that there have to be, either implicit or explicit, g_in' and g_in
        stated somewhere. This method collects all non explicitly defined elements and adds them to the model.
        """
        from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
        from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
        from pynestml.modelprocessor.ASTVariable import ASTVariable
        from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
        from pynestml.modelprocessor.ASTSimpleExpression import ASTSimpleExpression
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

    @staticmethod
    def mark_conductance_based_buffers(_input_lines):
        # type: (Generator[ASTInputLine,List[ASTInputBlock],None]) -> None
        from pynestml.modelprocessor.PredefinedTypes import PredefinedTypes
        from pynestml.modelprocessor.Symbol import SymbolKind
        # this is the updated version, where nS buffers are marked as conductance based
        for bufferDeclaration in _input_lines:
            if bufferDeclaration.isSpike():
                symbol = bufferDeclaration.getScope().resolveToSymbol(bufferDeclaration.getName(), SymbolKind.VARIABLE)
                if symbol is not None and symbol.getTypeSymbol().equals(PredefinedTypes.getTypeIfExists('nS')):
                    symbol.setConductanceBased(True)
        return

    def assign_ode_to_variables(self, _ode_block):
        # type: (ASTEquationsBlock) -> None
        from pynestml.modelprocessor.ASTOdeEquation import ASTOdeEquation
        from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
        for decl in _ode_block.getDeclarations():
            if isinstance(decl, ASTOdeEquation):
                self.add_ode_to_variable(decl)
            if isinstance(decl, ASTOdeShape):
                self.add_ode_shape_to_variable(decl)
        return

    @staticmethod
    def add_ode_to_variable(_ode_equation):
        # type: (ASTOdeEquation) -> None
        from pynestml.modelprocessor.Symbol import SymbolKind
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

    @staticmethod
    def add_ode_shape_to_variable(_ode_shape):
        # type: (ASTOdeShape) -> None
        from pynestml.modelprocessor.Symbol import SymbolKind
        from pynestml.modelprocessor.VariableSymbol import VariableType
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
