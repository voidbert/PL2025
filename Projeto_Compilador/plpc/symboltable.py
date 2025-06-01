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

from pprint import pprint

import ply.lex

# pylint: disable-next=wildcard-import,unused-wildcard-import
from .ast import *
from .error import print_error

class SymbolTableError(ValueError):
    pass

SymbolValue = \
    LabelDefinition | CallableDefinition | ConstantDefinition | TypeDefinition | VariableDefinition

class SymbolTable:
    def __init__(self, file_path: str, lexer: ply.lex.Lexer) -> None:
        self.file_path = file_path
        self.lexer = lexer

        empty_body = Block([], [], [], [], [], [])

        self.scopes: list[dict[str, SymbolValue]] = [
            # 6.2.2.10 - Required identifiers are in the scope of the program
            # 6.4.2 - Required simple types
            {
                'integer': TypeDefinition('integer', BuiltInType.INTEGER),
                'real': TypeDefinition('real', BuiltInType.REAL),
                'boolean': TypeDefinition('boolean', BuiltInType.BOOLEAN),
                'char': TypeDefinition('char', BuiltInType.CHAR),
                'true': ConstantDefinition('true', True),
                'false': ConstantDefinition('false', False),
                'maxint': ConstantDefinition('maxint', 1 << 16 - 1),
                'write': CallableDefinition('write', None, None, empty_body),
                'writeln': CallableDefinition('writeln', None, None, empty_body),
                'read': CallableDefinition('read', None, None, empty_body),
                'readln': CallableDefinition('readln', None, None, empty_body),

                # Non-standard
                'string': TypeDefinition('char', BuiltInType.STRING),
                'length': CallableDefinition('length',
                                             [
                                                VariableDefinition('str', BuiltInType.STRING, True)
                                             ],
                                             VariableDefinition(
                                                'length', BuiltInType.INTEGER, True),
                                             empty_body),
            }
        ]

    def new_scope(self) -> None:
        self.scopes.append({})

    def unstack_top_scope(self) -> None:
        self.scopes.pop()

    def query(self,
              identifier: str,
              lexspan: tuple[int, int] = (0, 0),
              error: bool = False,
              target_object_name: str = 'Object') -> tuple[None | SymbolValue, bool]:

        identifier_lower = identifier.lower()

        for i, scope in enumerate(reversed(self.scopes)):
            scope_result = scope.get(identifier_lower)
            if scope_result is not None:
                return scope_result, i == 0

        if error:
            print_error(self.file_path,
                        self.lexer.lexdata,
                        f'{target_object_name} \'{identifier}\' not found',
                        self.lexer.lineno,
                        lexspan[0],
                        lexspan[1] - lexspan[0] + 1)
            raise SymbolTableError()

        return None, False

    def query_label(self,
                    identifier: int,
                    lexspan: tuple[int, int] = (0, 0),
                    error: bool = False) -> LabelDefinition:

        query_result, top_scope = self.query(str(identifier), lexspan, error, 'Label')

        if not isinstance(query_result, LabelDefinition):
            print_error(self.file_path,
                        self.lexer.lexdata,
                        f'Object with name \'{identifier}\' is not a label',
                        self.lexer.lineno,
                        lexspan[0],
                        lexspan[1] - lexspan[0] + 1)
            raise SymbolTableError()
        elif not top_scope:
            pprint(self.scopes)
            print_error(self.file_path,
                        self.lexer.lexdata,
                        f'Label \'{identifier}\' not in the top-most scope',
                        self.lexer.lineno,
                        lexspan[0],
                        lexspan[1] - lexspan[0] + 1)
            raise SymbolTableError()

        return query_result

    def query_constant(self,
                       identifier: str,
                       lexspan: tuple[int, int] = (0, 0),
                       error: bool = False) -> tuple[None | ConstantDefinition, bool]:

        query_result, top_scope = self.query(identifier, lexspan, error, 'Constant')

        if not isinstance(query_result, ConstantDefinition):
            print_error(self.file_path,
                        self.lexer.lexdata,
                        f'Object with name \'{identifier}\' is not a constant',
                        self.lexer.lineno,
                        lexspan[0],
                        lexspan[1] - lexspan[0] + 1)
            raise SymbolTableError()

        return query_result, top_scope

    def query_type(self,
                   identifier: str,
                   lexspan: tuple[int, int] = (0, 0),
                   error: bool = False) -> tuple[None | TypeDefinition, bool]:

        query_result, top_scope = self.query(identifier, lexspan, error, 'Type')

        if not isinstance(query_result, TypeDefinition):
            print_error(self.file_path,
                        self.lexer.lexdata,
                        f'Object with name \'{identifier}\' is not a type',
                        self.lexer.lineno,
                        lexspan[0],
                        lexspan[1] - lexspan[0] + 1)
            raise SymbolTableError()

        return query_result, top_scope

    def query_variable(self,
                       identifier: str,
                       lexspan: tuple[int, int] = (0, 0),
                       error: bool = False) -> tuple[None | VariableDefinition, bool]:

        query_result, top_scope = self.query(identifier, lexspan, error, 'Variable')

        if not isinstance(query_result, VariableDefinition):
            print_error(self.file_path,
                        self.lexer.lexdata,
                        f'Object with name \'{identifier}\' is not a variable',
                        self.lexer.lineno,
                        lexspan[0],
                        lexspan[1] - lexspan[0] + 1)
            raise SymbolTableError()

        return query_result, top_scope

    def query_callable(self,
                       identifier: str,
                       lexspan: tuple[int, int] = (0, 0),
                       error: bool = False) -> tuple[None | CallableDefinition, bool]:

        query_result, top_scope = self.query(identifier, lexspan, error, 'Callable')

        if not isinstance(query_result, CallableDefinition):
            print_error(self.file_path,
                        self.lexer.lexdata,
                        f'Object with name \'{identifier}\' is not a callable',
                        self.lexer.lineno,
                        lexspan[0],
                        lexspan[1] - lexspan[0] + 1)
            raise SymbolTableError()

        return query_result, top_scope

    def add(self, value: SymbolValue, lexspan: tuple[int, int]) -> None:
        name = str(value.name) if isinstance(value, LabelDefinition) else value.name
        query_result, top_scope = self.query(name)

        if query_result is not None:
            if top_scope:
                print_error(self.file_path,
                            self.lexer.lexdata,
                            f'Object with name \'{name}\' already exists in this scope',
                            self.lexer.lineno,
                            lexspan[0],
                            lexspan[1] - lexspan[0] + 1)

                raise SymbolTableError()
            else:
                print_error(self.file_path,
                            self.lexer.lexdata,
                            f'Shadowing object with name \'{name}\'',
                            self.lexer.lineno,
                            lexspan[0],
                            lexspan[1] - lexspan[0] + 1,
                            True)
                self.scopes[-1][name.lower()] = value
        else:
            self.scopes[-1][name.lower()] = value
