# -------------------------------------------- LICENSE --------------------------------------------
#
# Copyright 2025 Humberto Gomes, José Lopes, José Matos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -------------------------------------------------------------------------------------------------

from typing import Any, Callable

import ply.lex
import ply.yacc

# pylint: disable-next=wildcard-import,unused-wildcard-import
from .ast import *
from .error import print_error
from .lexer import create_lexer
from .symboltable import SymbolTable, SymbolTableError
from .typechecker import TypeChecker, TypeCheckerError

class ParserError(ValueError):
    pass

class _Parser:
    def __init__(self, file_path: str, start_production: str):
        self.file_path = file_path
        self.has_errors = False

        self.lexer = create_lexer(file_path)
        self.tokens = list(self.lexer.lextokens)
        self.parser = ply.yacc.yacc(module=self,
                                    start=start_production,
                                    debug=False,
                                    write_tables=False)

        self.symbols = SymbolTable(file_path, self.lexer)
        self.type_checker = TypeChecker(file_path, self.lexer)

    def print_error(self,
                    error_message: str,
                    start: int,
                    length: int,
                    warning: bool = False) -> None:

        print_error(self.file_path,
                    self.lexer.lexdata,
                    error_message,
                    self.lexer.lineno,
                    start,
                    length,
                    warning)

        if not warning:
            self.has_errors = True

    # 6.2 - Blocks, scopes and activations

    def p_program(self, p: ply.yacc.YaccProduction) -> None:
        '''
        program : PROGRAM ID program-arguments ';' block '.'
        '''
        p[0] = Program(p[2], p[5])

    # Continue parsing even if program arguments are invalid
    def p_program_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        program : PROGRAM ID error ';' block '.'
        '''

    def p_program_arguments_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        program-arguments :
        '''

    def p_program_arguments_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        program-arguments : '(' ')'
        '''
        self.print_error('Invalid program arguments: at least one argument required',
                         p.lexspan(0)[0],
                         p.lexspan(0)[1] - p.lexspan(0)[0] + 1)

    def p_program_arguments_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        program-arguments : '(' identifier-list ')'
        '''
        self.print_error('Program arguments are not supported. Ignoring them...',
                         p.lexspan(0)[0],
                         p.lexspan(0)[1] - p.lexspan(0)[0] + 1,
                         True)

    def p_identitifier_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        identifier-list : ID
        '''
        p[0] = [(p[1], p.lexspan(1)[0])]

    def p_identitifier_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        identifier-list : identifier-list ',' ID
        '''
        p[1].append((p[3], p.lexspan(3)[0]))
        p[0] = p[1]

    def p_block(self, p: ply.yacc.YaccProduction) -> None:
        '''
        block : any-block-list begin-end-statement
        '''

        blocks: dict[str, int | None] = {
            'LABEL': None,
            'CONST': None,
            'TYPE': None,
            'VAR': None,
            'CALL': None
        }

        for i, ((block_type, _), start) in enumerate(p[1]):
            for before in list(blocks):
                if before == block_type:
                    break
                elif blocks[before] is None:
                    blocks[before] = -1

            if blocks[block_type] is None:
                blocks[block_type] = i
            elif blocks[block_type] == -1:
                self.print_error(
                    'Blocks in the wrong order. Correct order is '
                    'LABEL, CONST, TYPE, VAR, PROCEDURE / FUNCTION',
                    start,
                    len(block_type)
                )
            else:
                self.print_error(f'{block_type} block defined twice',
                                 start,
                                 len(block_type))

        def get_block(name: str) -> list:
            index = blocks[name]
            if index is None or index == -1:
                return []
            else:
                return p[1][index][0][1]

        p[0] = Block(
            get_block('LABEL'),
            get_block('CONST'),
            get_block('TYPE'),
            get_block('VAR'),
            get_block('CALL'),
            p[2]
        )

        if get_block('LABEL') is not None:
            for label in get_block('LABEL'):
                if label.used and label.statement is None:
                    self.print_error(
                        f'Label \'{label.name}\' was used but not assigned to any statement',
                        p.lexspan(1)[0],
                        len('LABEL')
                    )

    def p_any_block_list_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        any-block-list :
        '''
        p[0] = []

    def p_any_block_list_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        any-block-list : any-block-list-non-empty
        '''
        p[0] = p[1]

    def p_any_block_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        any-block-list-non-empty : any-block
        '''
        p[0] = [(p[1], p.lexspan(1)[0])]

    def p_any_block_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        any-block-list-non-empty : any-block-list any-block
        '''
        p[1].append((p[2], p.lexspan(2)[0]))
        p[0] = p[1]

    def p_any_block(self, p: ply.yacc.YaccProduction) -> None:
        '''
        any-block : label-block
                  | constant-block
                  | type-block
                  | variable-block
                  | callable-block
        '''
        p[0] = p[1]

    def p_label_block(self, p: ply.yacc.YaccProduction) -> None:
        '''
        label-block : LABEL label-list ';'
        '''
        p[0] = ('LABEL', p[2])

    def p_label_block_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        label-block : LABEL
                    | LABEL ';'
        '''

        self.print_error('At least one label definition is required in a label block',
                         p.lexspan(0)[0],
                         len('LABEL'))
        p[0] = ('LABEL', [])

    def p_label_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        label-list : INTEGER
        '''
        p[0] = [self.__add_label(p, 1)]

    def p_label_definition_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        label-list : label-list ',' INTEGER
        '''
        p[1].append(self.__add_label(p, 3))
        p[0] = p[1]

    def __add_label(self, p: ply.yacc.YaccProduction, i: int) -> LabelDefinition:
        try:
            label = LabelDefinition(p[i], None)
            self.symbols.add(label, (p.lexspan(i)[0], p.lexspan(i)[0] + len(str(p[i])) - 1))
        except SymbolTableError:
            self.has_errors = True

        return label

    # 6.3 - Constant definitions

    def p_constant_block(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant-block : CONST constant-definition-list
        '''
        p[0] = ('CONST', p[2])

    def p_constant_block_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant-block : CONST
                       | CONST ';'
        '''

        self.print_error('At least one constant definition is required in a constant block',
                         p.lexspan(0)[0],
                         len('CONST'))
        p[0] = ('CONST', [])

    def p_constant_definition_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant-definition-list : constant-definition
        '''
        p[0] = [p[1]]

    def p_constant_definition_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant-definition-list : constant-definition-list constant-definition
        '''
        p[1].append(p[2])
        p[0] = p[1]

    def p_constant_definition(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant-definition : ID '=' constant ';'
        '''
        p[0] = ConstantDefinition(p[1], p[3])

        try:
            self.symbols.add(p[0], (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1]) - 1))
        except SymbolTableError:
            self.has_errors = True

    def p_constant(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant : unsigned-constant
                 | signed-constant
        '''
        p[0] = p[1]

    def p_constant_expression_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant : expression
        '''
        self.print_error('In standard Pascal, full expressions are not allowed in constants',
                         p.lexspan(0)[0],
                         p.lexspan(0)[1] - p.lexspan(0)[0] + 1)

    def p_unsigned_constant_id(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unsigned-constant : ID
        '''

        try:
            query_result, _ = self.symbols.query_constant(
                p[1],
                (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1]) - 1),
                True
            )

            assert query_result is not None
            p[0] = query_result.value
        except SymbolTableError:
            self.has_errors = True

    def p_unsigned_constant_literal(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unsigned-constant : unsigned-constant-literal
        '''
        p[0] = p[1]

    def p_unsigned_constant_literal_literal(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unsigned-constant-literal : FLOAT
                                  | INTEGER
                                  | STRING
        '''
        p[0] = p[1]

    def p_signed_constant_sign(self, p: ply.yacc.YaccProduction) -> None:
        '''
        signed-constant : '+' unsigned-constant
                        | '-' unsigned-constant
        '''

        try:
            constant_type = self.type_checker.get_constant_type(p[2])
            _ = self.type_checker.get_unary_operation_type(
                UnaryOperation(p[1], (p[2], constant_type)),
                (p.lexspan(0)[0], p.lexspan(0)[0])
            )

            multiplier = 1 if p[1] == '+' else -1
            p[0] = multiplier * p[2]
        except TypeCheckerError:
            self.has_errors = True

    # 6.4 - Type definitions

    def p_type_block(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type-block : TYPE type-definition-list
        '''
        p[0] = ('TYPE', p[2])

    def p_type_block_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type-block : TYPE
                   | TYPE ';'
        '''

        self.print_error('At least one type definition is required in a type block',
                         p.lexspan(0)[0],
                         len('TYPE'))
        p[0] = ('TYPE', [])

    def p_type_definition_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type-definition-list : type-definition
        '''
        p[0] = [p[1]]

    def p_type_definition_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type-definition-list : type-definition-list type-definition
        '''
        p[1].append(p[2])
        p[0] = p[1]

    def p_type_definition(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type-definition : ID '=' type ';'
        '''

        type_definition = TypeDefinition(p[1], p[3])
        p[0] = type_definition

        if isinstance(p[3], list):
            # Enumerated type
            for constant in p[3]:
                constant.value.constant_type = type_definition

        try:
            self.symbols.add(p[0], (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1]) - 1))
        except SymbolTableError:
            self.has_errors = True

    def p_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type : type-id
             | pointer-type
             | enumerated-type
             | structured-type
        '''
        p[0] = p[1]

    def p_type_range(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type : range-type
        '''

        if p[1] is not None:
            self.print_error(
                'Range type being interpreted as the type of its components',
                p.lexspan(0)[0],
                self.lexer.lexpos - p.lexspan(0)[0],
                True
            )
            p[0] = p[1].subtype

    def p_type_id(self, p: ply.yacc.YaccProduction) -> None:
        '''
        type-id : ID
        '''

        try:
            query_result, _ = self.symbols.query_type(
                p[1],
                (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1]) - 1),
                True
            )

            assert query_result is not None
            p[0] = query_result.value
        except SymbolTableError:
            self.has_errors = True

    def p_pointer_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        pointer-type : '^' type-id
        '''
        self.print_error('Pointer types are not supported', p.lexspan(0)[0], len('^'))

    def p_enumerated_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        enumerated-type : '(' identifier-list ')'
        '''

        ret: list[ConstantDefinition] = []
        for i, (identifier, start) in enumerate(p[2]):
            try:
                value = EnumeratedTypeConstantValue(identifier, i, None) # type is set later
                constant = ConstantDefinition(identifier, value)
                self.symbols.add(constant, (start, start + len(identifier) - 1))

                ret.append(constant)
            except SymbolTableError:
                self.has_errors = True

        p[0] = ret

    def p_range_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        range-type : constant RANGE constant
        '''

        try:
            type1 = self.type_checker.get_constant_type(p[1])
            type2 = self.type_checker.get_constant_type(p[3])

            if type1 != type2:
                self.print_error('Types of elements in range type are different',
                                 p.lexspan(0)[0],
                                 p.lexspan(0)[1] - p.lexspan(0)[0] + 1)

                p[0] = RangeType(1, 1, BuiltInType.INTEGER)
                return
        except TypeCheckerError:
            self.has_errors = True
            p[0] = RangeType(1, 1, BuiltInType.INTEGER)
            return

        try:
            value1 = self.type_checker.get_constant_ordinal_value(p[1])
            value2 = self.type_checker.get_constant_ordinal_value(p[3])
        except TypeCheckerError:
            self.print_error('Type of elements in range type is not ordinal',
                             p.lexspan(0)[0],
                             p.lexspan(0)[1] - p.lexspan(0)[0] + 1)

            p[0] = RangeType(1, 1, BuiltInType.INTEGER)
            return

        if value1 > value2:
            self.print_error('Range\'s upper bound is lower than its lower bound',
                             p.lexspan(0)[0],
                             p.lexspan(0)[1] - p.lexspan(0)[0] + 1)

            p[0] = RangeType(1, 1, BuiltInType.INTEGER)
            return

        p[0] = RangeType(p[1], p[3], self.type_checker.get_constant_type(p[1]))

    def p_structured_type_unpacked(self, p: ply.yacc.YaccProduction) -> None:
        '''
        structured-type : unpacked-structured-type
        '''
        p[0] = p[1]

    def p_structured_type_packed(self, p: ply.yacc.YaccProduction) -> None:
        '''
        structured-type : PACKED unpacked-structured-type
        '''

        self.print_error('Packed structured types are not supported. Ignoring this keyword ...',
                         p.lexspan(0)[0],
                         len('PACKED'),
                         True)
        p[0] = p[2]

    def p_unpacked_structured_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unpacked-structured-type : array-type
                                 | record-type
                                 | set-type
                                 | file-type
        '''
        p[0] = p[1]

    def p_array_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        array-type : ARRAY '[' array-dimensions ']' OF type
        '''
        if isinstance(p[6], ArrayType):
            p[3].extend(p[6].dimensions)
            p[0] = ArrayType(p[6].subtype, p[3])
        else:
            p[0] = ArrayType(p[6], p[3])

    def p_array_incomplete(self, p: ply.yacc.YaccProduction) -> None:
        '''
        array-type : ARRAY OF type
        '''
        self.print_error('Missing array dimensions', p.lexspan(0)[0], len('ARRAY'))

    def p_array_dimensions_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        array-dimensions : range-type
        '''
        p[0] = [p[1]]

    def p_array_dimensions_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        array-dimensions : array-dimensions ',' range-type
        '''
        p[1].append(p[3])
        p[0] = p[1]

    def p_record_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        record-type : RECORD
        '''
        self.print_error('Record types are not supported', p.lexspan(0)[0], len('RECORD'))

        count = 1
        while True:
            tok = self.parser.token()
            if tok.type == 'BEGIN':
                count += 1
            elif tok.type == 'END':
                count -= 1

            if not tok or count == 0:
                self.parser.errok()
                break

    def p_set_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        set-type : SET OF type
        '''
        self.print_error('Set types are not supported', p.lexspan(0)[0], len('SET'))

    def p_file_type(self, p: ply.yacc.YaccProduction) -> None:
        '''
        file-type : FILE OF type
        '''
        self.print_error('File types are not supported', p.lexspan(0)[0], len('FILE'))

    # 6.5 - Declarations and denotations of variables

    def p_variable_block(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-block : VAR variable-definition-list
        '''
        p[0] = ('VAR', p[2])

    def p_variable_block_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-block : VAR
                       | VAR ';'
        '''

        self.print_error(
            'At least one variable definition is required in a variable block',
            p.lexspan(0)[0],
            len('VAR')
        )
        p[0] = ('VAR', [])

    def p_variable_definition_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-definition-list : variable-definition
        '''
        p[0] = p[1]

    def p_variable_definition_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-definition-list : variable-definition-list variable-definition
        '''
        p[1].extend(p[2])
        p[0] = p[1]

    def p_variable_definition(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-definition : identifier-list ':' type ';'
        '''

        ret: list[VariableDefinition] = []
        for identifier, start in p[1]:
            try:
                variable = VariableDefinition(identifier, p[3], len(self.symbols.scopes) == 2)
                self.symbols.add(variable, (start, start + len(identifier) - 1))
                ret.append(variable)
            except SymbolTableError:
                self.has_errors = True

        p[0] = ret

    def p_variable_usage(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-usage : ID variable-index-list
        '''
        try:
            definition, _ = self.symbols.query_variable(
                p[1],
                (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1])),
                True
            )
            assert definition is not None

            current_type = definition.variable_type
            for _, index_type in p[2][1]:
                try:
                    current_type = self.type_checker.type_after_indexation(
                        current_type,
                        index_type,
                        p.lexspan(0)
                    )
                except TypeCheckerError:
                    self.has_errors = True
                    break

            p[0] = VariableUsage(definition, current_type, p[2][1])
        except SymbolTableError:
            self.has_errors = True

    def p_variable_index_list_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-index-list :
        '''
        p[0] = ('VAR', [])

    def p_variable_index_list_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-index-list : variable-indices
        '''
        p[0] = ('VAR', p[1])

    def p_variable_indices_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-indices : variable-index
        '''
        p[0] = p[1]

    def p_variable_indices_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-indices : variable-indices variable-index
        '''
        p[1].extend(p[2])
        p[0] = p[1]

    def p_variable_index(self, p: ply.yacc.YaccProduction) -> None:
        '''
        variable-index : '[' expression-list ']'
        '''
        p[0] = p[2]

    # 6.6. Procedure and function delarations
    # NOTE: recursivity is not supported

    def p_callable_block(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-block : callable-list ';'
        '''

        if len(self.symbols.scopes) > 1:
            if p[1] is not None and len(p[1]) > 0 and p[1][0] is not None:
                first_token_length = \
                    len('PROCEDURE') if p[1][0].return_variable is None else len('FUNCTION')
            else:
                first_token_length = len('PROCEDURE') # On failure, just guess

            self.print_error(
                'Nested procedures / functions are not supported',
                p.lexspan(0)[0],
                first_token_length
            )

        p[0] = ('CALL', p[1])

    def p_callable_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-list : callable-definition
        '''
        p[0] = [p[1]]

    def p_callable_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-list : callable-list callable-definition
        '''
        p[1].append(p[2])
        p[0] = p[1]

    def p_callable_definition_procedure(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-definition : procedure-heading ';' block
        '''

        call = CallableDefinition(
            p[1][0],
            p[1][1],
            None,
            p[3]
        )
        self.symbols.unstack_top_scope()

        try:
            self.symbols.add(call, (p[1][2], p[1][2] + len(p[1][0]) - 1))
            p[0] = call
        except SymbolTableError:
            self.has_errors = True

    def p_callable_definition_function(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-definition : function-heading ';' block
        '''

        call = CallableDefinition(
            p[1][0],
            p[1][1],
            p[1][2],
            p[3]
        )
        self.symbols.unstack_top_scope()

        try:
            self.symbols.add(call, (p[1][3], p[1][3] + len(p[1][0]) - 1))
            p[0] = call
        except SymbolTableError:
            self.has_errors = True

    def p_callable_definition_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-definition : error
        '''

    def p_new_scope_procedure(self, p: ply.yacc.YaccProduction) -> None:
        '''
        procedure-heading : PROCEDURE ID new-scope parameter-list
        '''
        p[0] = (p[2], p[4], p.lexspan(2)[0])

    def p_function_heading(self, p: ply.yacc.YaccProduction) -> None:
        '''
        function-heading : FUNCTION ID new-scope parameter-list ':' type-id
        '''
        variable = VariableDefinition(p[2], p[6], True)
        self.symbols.add(variable, p.lexspan(2))
        p[0] = (p[2], p[4], variable, p.lexspan(2)[0])

    def p_new_scope(self, _: ply.yacc.YaccProduction) -> None:
        '''
        new-scope :
        '''
        self.symbols.new_scope()

    def p_parameter_list_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        parameter-list :
        '''
        p[0] = []

    def p_parameter_list_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        parameter-list : '(' parameter-list-non-empty ')'
        '''
        p[0] = p[2]

    def p_parameter_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        parameter-list-non-empty : parameter
        '''
        p[0] = p[1]

    def p_parameter_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        parameter-list-non-empty : parameter-list-non-empty ';' parameter
        '''
        p[1].extend(p[3])
        p[0] = p[1]

    def p_parameter(self, p: ply.yacc.YaccProduction) -> None:
        '''
        parameter : identifier-list ':' type-id
        '''

        ret: list[VariableDefinition] = []
        for identifier, start in p[1]:
            try:
                variable = VariableDefinition(identifier, p[3], True)
                self.symbols.add(variable, (start, start + len(identifier) - 1))
                ret.append(variable)
            except SymbolTableError:
                self.has_errors = True

        p[0] = ret

    def p_callable_call(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-call : ID callable-arguments
        '''

        ordinals = {
            '1': 'st',
            '2': 'nd',
            '3': 'rd'
        }

        try:
            definition, _ = self.symbols.query_callable(
                p[1],
                (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1]) - 1),
                True
            )
            assert definition is not None

            if definition.parameters is not None:
                expected_parameters = len(definition.parameters)
                got_parameters = len(p[2][1])

                if expected_parameters != got_parameters:
                    self.print_error(
                        'Wrong number of arguments: '
                        f'expected {expected_parameters}, got {got_parameters}',
                        p.lexspan(1)[0],
                        len(p[1])
                    )

                for i, (left, right) in enumerate(zip(definition.parameters, p[2][1])):
                    if right:
                        if not self.type_checker.can_assign(left.variable_type, right[1]):
                            ordinal = ordinals.get(str(i + 1)[-1], 'th')
                            self.print_error(
                                f'Type mismatch in {i + 1}{ordinal} argument',
                                p.lexspan(1)[0],
                                len(p[1])
                            )
                        elif left.variable_type == BuiltInType.STRING and \
                            right[1] == BuiltInType.CHAR:

                            p[2][1][i] = (p[2][1][i][0], BuiltInType.STRING)
            elif definition.name in ['writeln', 'write']:
                for i, parameter in enumerate(p[2][1]):
                    if parameter and isinstance(parameter[1], ArrayType):
                        ordinal = ordinals.get(str(i + 1)[-1], 'th')
                        self.print_error(
                            f'Type mismatch in {i + 1}{ordinal} argument: must be ordinal type',
                            p.lexspan(1)[0],
                            len(p[1])
                        )

            elif definition.name == 'readln':
                for i, parameter in enumerate(p[2][1]):
                    if parameter and (
                            not isinstance(parameter[0], VariableUsage) or
                            isinstance(parameter[1], ArrayType)
                        ):
                        ordinal = ordinals.get(str(i + 1)[-1], 'th')
                        self.print_error(
                            f'Type mismatch in {i + 1}{ordinal} argument: '
                            'must be an ordinal variable',
                            p.lexspan(1)[0],
                            len(p[1])
                        )

            p[0] = CallableCall(definition, p[2][1])
        except SymbolTableError:
            self.has_errors = True

    def p_callable_arguments_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-arguments :
        '''
        p[0] = ('CALL', [])

    def p_callable_arguments_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-arguments : '(' expression-list ')'
        '''
        p[0] = ('CALL', p[2])

    def p_callable_arguments_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        callable-arguments : '(' ')'
        '''
        self.print_error(
            'To pass no arguments, remove the parentheses',
            p.lexspan(1)[0],
            p.lexspan(2)[1] - p.lexspan(1)[0] + 1
        )
        p[0] = ('CALL', [])

    # 6.7 - Expressions

    def p_expression_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        expression : non-relational-expression
        '''
        p[0] = p[1]

    def p_expression_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        expression : non-relational-expression relational-operator non-relational-expression
        '''

        try:
            operation = BinaryOperation(p[2], p[1], p[3])
            expression_type = self.type_checker.get_binary_operation_type(operation, p.lexspan(2))
            p[0] = (operation, expression_type)
        except TypeCheckerError:
            self.has_errors = True

    def p_relational_operator(self, p: ply.yacc.YaccProduction) -> None:
        '''
        relational-operator : '='
                            | DIFFERENT
                            | '<'
                            | '>'
                            | LE
                            | GE
                            | IN
        '''
        p[0] = p[1].lower()

    def p_non_relational_expression_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        non-relational-expression : first-term
        '''
        p[0] = p[1]

    def p_non_relational_expression_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        non-relational-expression : non-relational-expression adding-operator term
        '''

        try:
            operation = BinaryOperation(p[2], p[1], p[3])
            expression_type = self.type_checker.get_binary_operation_type(operation, p.lexspan(2))
            p[0] = (operation, expression_type)
        except TypeCheckerError:
            self.has_errors = True

    def p_adding_operator(self, p: ply.yacc.YaccProduction) -> None:
        '''
        adding-operator : '+'
                        | '-'
                        | OR
        '''
        p[0] = p[1].lower()

    def p_first_term_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        first-term : first-factor
        '''
        p[0] = p[1]

    def p_first_term_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        first-term : first-term multiplying-operator factor
        '''

        try:
            operation = BinaryOperation(p[2], p[1], p[3])
            expression_type = self.type_checker.get_binary_operation_type(operation, p.lexspan(2))
            p[0] = (operation, expression_type)
        except TypeCheckerError:
            self.has_errors = True

    def p_first_factor_signed(self, p: ply.yacc.YaccProduction) -> None:
        '''
        first-factor : '+' factor
                     | '-' factor
        '''

        try:
            operation = UnaryOperation(p[1], p[2])
            expression_type = self.type_checker.get_unary_operation_type(operation, p.lexspan(1))
            p[0] = (operation, expression_type)
        except TypeCheckerError:
            self.has_errors = True

    def p_first_factor_unsigned(self, p: ply.yacc.YaccProduction) -> None:
        '''
        first-factor : factor
        '''
        p[0] = p[1]

    def p_term_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        term : factor
        '''
        p[0] = p[1]

    def p_term_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        term : term multiplying-operator factor
        '''

        try:
            operation = BinaryOperation(p[2], p[1], p[3])
            expression_type = self.type_checker.get_binary_operation_type(operation, p.lexspan(2))
            p[0] = (operation, expression_type)
        except TypeCheckerError:
            self.has_errors = True

    def p_multiplying_operator(self, p: ply.yacc.YaccProduction) -> None:
        '''
        multiplying-operator : '*'
                             | '/'
                             | DIV
                             | MOD
                             | AND
        '''
        p[0] = p[1].lower()

    def p_factor_parentheses(self, p: ply.yacc.YaccProduction) -> None:
        '''
        factor : '(' expression ')'
        '''
        p[0] = p[2]

    def p_factor_nil(self, p: ply.yacc.YaccProduction) -> None:
        '''
        factor : NIL
        '''
        self.print_error(
            'Pointer types are not supported',
            p.lexspan(0)[0],
            len('NIL')
        )

    def p_factor_not(self, p: ply.yacc.YaccProduction) -> None:
        '''
        factor : NOT factor
        '''

        try:
            operation = UnaryOperation(p[1].lower(), p[2])
            expression_type = self.type_checker.get_unary_operation_type(operation, p.lexspan(0))
            p[0] = (operation, expression_type)
        except TypeCheckerError:
            self.has_errors = True

    def p_factor_constant_literal(self, p: ply.yacc.YaccProduction) -> None:
        '''
        factor : unsigned-constant-literal
        '''
        p[0] = (p[1], self.type_checker.get_constant_type(p[1]))

    def p_factor_id(self, p: ply.yacc.YaccProduction) -> None:
        '''
        factor : ID variable-index-list
               | ID callable-arguments
        '''

        try:
            obj, _ = self.symbols.query(
                p[1],
                (p.lexspan(1)[0], p.lexspan(1)[0] + len(p[1]) - 1),
                True
            )
            assert obj is not None

            if isinstance(obj, ConstantDefinition):
                if len(p[2][1]) == 0:
                    p[0] = (obj.value, self.type_checker.get_constant_type(obj.value))
                else:
                    action = 'call' if p[2][0] == 'CALL' else 'index'
                    self.print_error(
                        f'Attempting to {action} constant',
                        p.lexspan(0)[0],
                        len(p[1])
                    )
            elif isinstance(obj, VariableDefinition):
                if p[2][0] == 'VAR':
                    self.p_variable_usage(p)
                    p[0] = (p[0], p[0].type)
                else:
                    self.print_error(
                        'Attempting to call variable',
                        p.lexspan(0)[0],
                        len(p[1])
                    )
            elif isinstance(obj, CallableDefinition):
                if obj.return_variable is None:
                    self.print_error(
                        'This is a procedure and not a function',
                        p.lexspan(0)[0],
                        len(p[1])
                    )
                elif p[2][0] == 'CALL' or len(p[2][1]) == 0:
                    self.p_callable_call(p)
                    p[0] = (p[0], obj.return_variable.variable_type)
                else:
                    self.print_error(
                        'Attempting to index function',
                        p.lexspan(0)[0],
                        len(p[1])
                    )

        except SymbolTableError:
            self.has_errors = True

    def p_expression_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        expression-list : expression
        '''
        p[0] = [p[1]]

    def p_expression_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        expression-list : expression-list ',' expression
        '''
        p[1].append(p[3])
        p[0] = p[1]

    # 6.8 - Statements

    def p_begin_end_statement(self, p: ply.yacc.YaccProduction) -> None:
        '''
        begin-end-statement : BEGIN statement-list END
        '''
        p[0] = p[2]

    def p_begin_end_statement_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        begin-end-statement : BEGIN END
        '''
        self.print_error(
            'Empty compound statements are not allowed in standard Pascal',
            p.lexspan(1)[0],
            len('BEGIN')
        )

        p[0] = []

    def p_statement_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        statement-list : statement
        '''
        p[0] = [p[1]]

    def p_statement_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        statement-list : statement-list ';' statement
        '''
        p[1].append(p[3])
        p[0] = p[1]

    def p_statement_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        statement : unlabeled-statement
        '''
        if p[1] is None:
            p[0] = ([], None)
        else:
            p[0] = (p[1], None)

    def p_statement_labeled(self, p: ply.yacc.YaccProduction) -> None:
        '''
        statement : INTEGER ':' unlabeled-statement
        '''

        try:
            label = self.symbols.query_label(
                p[1],
                (p.lexspan(1)[0], p.lexspan(1)[0] + len(str(p[1])) - 1),
                True
            )

            if label.statement is None:
                label.statement = p[3]
            else:
                self.print_error(
                    'Label already assigned to a statement',
                    p.lexspan(1)[0],
                    len(str(p[1]))
                )

            if p[3] is None:
                p[0] = ([], label)
            else:
                p[0] = (p[3], label)
        except SymbolTableError:
            self.has_errors = True
            if p[3] is None:
                p[0] = ([], label)
            else:
                p[0] = (p[3], None)

    def p_unlabeled_statement_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement :
        '''

    def p_unlabeled_statement_assign(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : variable-usage ASSIGN expression
        '''

        if p[1] is not None and p[3] is not None:
            if p[1].variable.variable_type == BuiltInType.STRING and p[3][1] == BuiltInType.CHAR:
                p[3] = (p[3][0], BuiltInType.STRING)

            if not self.type_checker.can_assign(p[1].type, p[3][1]):
                self.print_error(
                    'Assignment is impossible due to type mismatch',
                    p.lexspan(2)[0],
                    len(':=')
                )

            try:
                self.type_checker.fail_on_string_indexation(
                    p[1],
                    (p.lexspan(2)[0], p.lexspan(2)[0] + 1)
                )
            except TypeCheckerError:
                self.has_errors = True

        p[0] = AssignStatement(p[1], p[3])

    def p_unlabeled_statement_assign_error(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : variable-usage '=' expression
        '''
        self.print_error('Syntax error. Did you mean to use \':=\'?', p.lexspan(2)[0], len('='))

    def p_unlabeled_statement_goto(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : GOTO INTEGER
        '''

        try:
            label = self.symbols.query_label(
                p[2],
                (p.lexspan(2)[0], p.lexspan(2)[0] + len(str(p[2])) - 1),
                True
            )
            label.used = True
            p[0] = GotoStatement(label)
        except SymbolTableError:
            self.has_errors = True

    def p_unlabeled_statement_call(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : callable-call
        '''

        if p[1] is not None and p[1].callable.return_variable is not None:
            self.print_error(
                'Calling a function, not a procedure',
                p.lexspan(0)[0],
                len(p[1].callable.name)
            )
        else:
            p[0] = p[1]

    def p_unlabeled_statement_begin_end(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : begin-end-statement
        '''
        p[0] = p[1]

    def p_unlabeled_statement_if(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : IF expression THEN statement if-statement-else
        '''
        if p[2] is not None and p[2][1] != BuiltInType.BOOLEAN:
            self.print_error(
                'Expression in if-statement is not boolean',
                p.lexspan(1)[0],
                len('IF')
            )
            p[0] = []

        p[0] = IfStatement(p[2], p[4], p[5])

    def p_if_statement_else_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        if-statement-else :
        '''
        p[0] = ([], None)

    def p_if_statement_else_non_empty(self, p: ply.yacc.YaccProduction) -> None:
        '''
        if-statement-else : ELSE statement
        '''
        p[0] = p[2]

    def p_unlabeled_statement_repeat(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : REPEAT statement-list UNTIL expression
        '''

        if p[4] is not None and p[4][1] != BuiltInType.BOOLEAN:
            self.print_error(
                'Expression in repeat-until loop is not boolean',
                p.lexspan(3)[0],
                len('UNTIL')
            )

        p[0] = RepeatStatement(p[4], p[2])

    def p_unlabeled_statement_while(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : WHILE expression DO statement
        '''

        if p[2] is not None and p[2][1] != BuiltInType.BOOLEAN:
            self.print_error(
                'Expression in while loop is not boolean',
                p.lexspan(1)[0],
                len('WHILE')
            )

        p[0] = WhileStatement(p[2], p[4])

    def p_unlabeled_statement_for(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : FOR ID ASSIGN expression TO     expression DO statement
                            | FOR ID ASSIGN expression DOWNTO expression DO statement
        '''

        try:
            definition, top_scope = self.symbols.query_variable(
                p[2],
                (p.lexspan(2)[0], p.lexspan(2)[0] + len(p[2]) - 1),
                True
            )
            assert definition is not None

            if not top_scope:
                self.print_error(
                    'For-loop control variable is not in the top-most scope',
                    p.lexspan(2)[0],
                    len(p[2])
                )

            if definition.variable_type not in \
                [BuiltInType.BOOLEAN, BuiltInType.INTEGER, BuiltInType.CHAR] and \
                not isinstance(definition.variable_type, list):

                self.print_error(
                    'For loop control variable is not ordinal',
                    p.lexspan(2)[0],
                    p.lexspan(2)[1] - p.lexspan(2)[0] + 1
                )

            if p[4] is not None and \
                not self.type_checker.can_assign(definition.variable_type, p[4][1]):

                self.print_error(
                    'Type mismatch between expression and loop control variable',
                    p.lexspan(4)[0],
                    p.lexspan(4)[1] - p.lexspan(4)[0] + 1
                )

            if p[6] is not None and \
                not self.type_checker.can_assign(definition.variable_type, p[6][1]):

                self.print_error(
                    'Type mismatch between expression and loop control variable',
                    p.lexspan(6)[0],
                    p.lexspan(6)[1] - p.lexspan(6)[0] + 1
                )

            p[0] = ForStatement(definition, p[4], p[6], p[5].lower(), p[8])
        except SymbolTableError:
            self.has_errors = True

    def p_case_statement(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : CASE expression OF case-element-list END
                            | CASE expression OF case-element-list ';' END
        '''
        p[0] = CaseStatement(p[2], p[4])

    def p_case_element_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        case-element-list : case-element
        '''
        p[0] = [p[1]]

    def p_case_element_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        case-element-list : case-element-list ';' case-element
        '''
        p[1].append(p[3])
        p[0] = p[1]

    def p_case_element(self, p: ply.yacc.YaccProduction) -> None:
        '''
        case-element : constant-list ':' statement
        '''
        p[0] = CaseElement(p[1], p[3])

    def p_constant_list_single(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant-list : constant
        '''
        p[0] = [p[1]]

    def p_constant_list_multiple(self, p: ply.yacc.YaccProduction) -> None:
        '''
        constant-list : constant-list ',' constant
        '''
        p[1].append(p[3])
        p[0] = p[1]

    def p_unlabeled_statement_with(self, p: ply.yacc.YaccProduction) -> None:
        '''
        unlabeled-statement : WITH variable-list DO statement
        '''
        self.print_error(
            'WITH statements are not supported',
            p.lexspan(1)[0],
            len('WITH')
        )

    def p_variable_list_single(self, _: ply.yacc.YaccProduction) -> None:
        '''
        variable-list : variable-usage
        '''

    def p_variable_list_multiple(self, _: ply.yacc.YaccProduction) -> None:
        '''
        variable-list : variable-list ',' variable-usage
        '''

    def p_error(self, t: None | ply.lex.LexToken) -> None:
        expected_tokens = self.parser.action[self.parser.state].keys()
        expected_tokens_str = ', '.join(t if len(t) > 1 else f'\'{t}\'' for t in expected_tokens)

        if t is None:
            self.print_error(
                f'Unexpected end-of-file. Expecting: {expected_tokens_str}',
                len(self.lexer.lexdata),
                1
            )
        else:
            string_value = t.value if isinstance(t.value, str) else t.value.string_value
            self.print_error(
                f'Unexpected token: \'{string_value}\'. Expecting: {expected_tokens_str}',
                t.lexpos,
                len(string_value)
            )

def create_parser(file_path: str,
                  start_production: str = 'program') -> ply.yacc.LRParser:

    def parse_wrapper(*args: str, **kwargs: Any) -> Callable[..., ply.yacc.LRParser]:
        ast = old_parse_fn(*args, tracking=True, **kwargs)
        if parser.has_errors:
            raise ParserError()

        return ast

    parser = _Parser(file_path, start_production)
    old_parse_fn = parser.parser.parse
    parser.parser.parse = parse_wrapper
    return parser.parser
