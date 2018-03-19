#
# ModelParser.py
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
from antlr4 import *
from pynestml.generated.PyNESTMLLexer import PyNESTMLLexer
from pynestml.generated.PyNESTMLParser import PyNESTMLParser
from typing import Union, Tuple

from pynestml.modelprocessor import ASTSymbolTableVisitor
from pynestml.modelprocessor.ASTAssignment import ASTAssignment
from pynestml.modelprocessor.ASTBuilderVisitor import ASTBuilderVisitor
from pynestml.modelprocessor.ASTCompoundStmt import ASTCompoundStmt
from pynestml.modelprocessor.ASTDeclaration import ASTDeclaration
from pynestml.modelprocessor.ASTExpression import ASTExpression
from pynestml.modelprocessor.ASTHigherOrderVisitor import ASTHigherOrderVisitor
from pynestml.modelprocessor.ASTNESTMLCompilationUnit import ASTNESTMLCompilationUnit
from pynestml.modelprocessor.ASTNode import ASTNode
from pynestml.modelprocessor.ASTOdeShape import ASTOdeShape
from pynestml.modelprocessor.ASTSmallStmt import ASTSmallStmt
from pynestml.modelprocessor.ASTSourcePosition import ASTSourcePosition
from pynestml.modelprocessor.SymbolTable import SymbolTable
from pynestml.utils.Logger import Logger, LOGGING_LEVEL
from pynestml.utils.Messages import Messages


class ModelParser(object):
    """
    This class contains several method used to parse handed over models and returns them as one or more AST trees.
    """

    @classmethod
    def parse_model_from_string(cls, _string):
        # type: (str) -> ASTNESTMLCompilationUnit
        builder, parser = cls._parse_input_stream(InputStream(_string))
        return cls._build_model(builder, parser)

    @classmethod
    def parse_model_from_file(cls, file_path):
        # type: (str) -> Union[ASTNESTMLCompilationUnit,None]
        try:
            input_file = FileStream(file_path)
        except IOError:
            print('(PyNestML.Parser) File ' + str(file_path) + ' not found. Processing is stopped!')
            return
        code, message = Messages.getStartProcessingFile(file_path)
        Logger.logMessage(_code=code, _message=message, _logLevel=LOGGING_LEVEL.INFO)
        builder, parser = cls._parse_input_stream(input_file)
        return cls._build_model(builder, parser)

    @classmethod
    def _build_model(cls, builder, parser):
        # type: (ASTBuilderVisitor, PyNESTMLParser) -> ASTNESTMLCompilationUnit
        compilation_unit = parser.nestmlCompilationUnit()
        ast = builder.visit(compilation_unit)
        SymbolTable.initializeSymbolTable(ast.getSourcePosition())
        for neuron in ast.getNeuronList():
            ASTSymbolTableVisitor.ASTSymbolTableVisitor.update_symbol_table(neuron)
            SymbolTable.addNeuronScope(neuron.getName(), neuron.getScope())
        return ast

    @classmethod
    def parse_expression(cls, _expression):
        # type: (str) -> ASTExpression
        builder, parser = cls._parse_input_stream(InputStream(_expression))
        ret = builder.visit(parser.expression())
        cls.set_source_positions(ret)
        return ret

    @classmethod
    def parse_declaration(cls, _declaration):
        # type: (str) -> ASTDeclaration
        builder, parser = cls._parse_input_stream(InputStream(_declaration))
        ret = builder.visit(parser.declaration())
        cls.set_source_positions(ret)
        return ret

    @classmethod
    def _parse_input_stream(cls, _input_stream):
        # type: (InputStream) -> Tuple[ASTBuilderVisitor,PyNESTMLParser]
        lexer = PyNESTMLLexer(_input_stream)
        stream = CommonTokenStream(lexer)
        stream.fill()
        parser = PyNESTMLParser(stream)
        builder = ASTBuilderVisitor(stream.tokens)
        return builder, parser

    @classmethod
    def parse_stmt(cls, _statement):
        # type: (str) -> Union[ASTSmallStmt,ASTCompoundStmt]
        builder, parser = cls._parse_input_stream(InputStream(_statement))
        ret = builder.visit(parser.stmt())
        cls.set_source_positions(ret)
        return ret

    @classmethod
    def parse_shape(cls, _shape):
        # type: (str) -> ASTOdeShape
        builder, parser = cls._parse_input_stream(InputStream(_shape))
        ret = builder.visit(parser.odeShape())
        cls.set_source_positions(ret)
        return ret

    @classmethod
    def set_source_positions(cls, _node):
        # type: (ASTNode) -> None
        ASTHigherOrderVisitor.visit(_node, lambda x: x.setSourcePosition(ASTSourcePosition.getAddedSourcePosition()))

    @classmethod
    def parse_assignment(cls, _assignment):
        # type: (str) -> ASTAssignment
        builder, parser = cls._parse_input_stream(InputStream(_assignment))
        ret = builder.visit(parser.assignment())
        cls.set_source_positions(ret)
        return ret
