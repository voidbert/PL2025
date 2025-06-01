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

import re
import ply.lex

from .error import print_error

class LexerError(ValueError):
    pass

class _Lexer:
    def __init__(self, file_path: str):
        self.has_errors = False                        # If errors have been detected by the lexer
        self.file_path = file_path                     # Path to the source for error printing
        self.last_error: tuple[int, int] | None = None # Start position and length of error

        self.literals = '.;:(,)<>=+-*/[]^'
        self.tokens = [
            # 6.1.2 - Keywords
            'PROGRAM', 'BEGIN', 'END',
            'LABEL', 'CONST', 'TYPE', 'VAR',
            'ARRAY', 'PACKED', 'SET', 'FILE', 'OF', 'RECORD',
            'FUNCTION', 'PROCEDURE',
            'IF', 'THEN', 'ELSE',
            'FOR', 'TO', 'DOWNTO', 'DO', 'WHILE', 'REPEAT', 'UNTIL',
            'CASE',
            'GOTO',
            'WITH',
            'AND', 'OR', 'NOT',
            'IN',
            'DIV', 'MOD',
            'NIL',

            # 6.1.2 - Special-symbols
            'DIFFERENT',
            'LE',
            'GE',
            'ASSIGN',
            'RANGE',

            # 6.1.3 - Identifiers
            'ID',

            # 6.1.4 - Directives
            # Not supported by the lexer (see ID)

            # 6.1.5 - Numbers
            'FLOAT',
            'INTEGER',

            # 6.1.6 - Labels
            # Not supported by the lexer (see INTEGER)

            # 6.1.7 - Character-strings
            'STRING',
         ]

        self.t_DIFFERENT = r'<>'
        self.t_LE = r'<='
        self.t_GE = r'>='
        self.t_ASSIGN = r':='
        self.t_RANGE = r'\.\.'

        self.t_ignore = ' \t\r'
        # 6.1.8 - Token separators
        self.t_ignore_COMMENT = r'({|\(\*)((?!{|\(\*)(.|\n))*?(}|\*\))'

        self.lexer = ply.lex.lex(module=self, reflags=re.IGNORECASE)

    def t_PROGRAM(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'PROGRAM\b'
        return t

    def t_BEGIN(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'BEGIN\b'
        return t

    def t_END(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'END\b'
        return t

    def t_LABEL(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'LABEL\b'
        return t

    def t_CONST(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'CONST\b'
        return t

    def t_TYPE(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'TYPE\b'
        return t

    def t_VAR(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'VAR\b'
        return t

    def t_ARRAY(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'ARRAY\b'
        return t

    def t_PACKED(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'PACKED\b'
        return t

    def t_SET(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'SET\b'
        return t

    def t_FILE(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'FILE\b'
        return t

    def t_OF(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'OF\b'
        return t

    def t_RECORD(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'RECORD\b'
        return t

    def t_FUNCTION(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'FUNCTION\b'
        return t

    def t_PROCEDURE(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'PROCEDURE\b'
        return t

    def t_IF(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'IF\b'
        return t

    def t_THEN(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'THEN\b'
        return t

    def t_ELSE(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'ELSE\b'
        return t

    def t_FOR(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'FOR\b'
        return t

    def t_TO(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'TO\b'
        return t

    def t_DOWNTO(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'DOWNTO\b'
        return t

    def t_DO(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'DO\b'
        return t

    def t_WHILE(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'WHILE\b'
        return t

    def t_REPEAT(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'REPEAT\b'
        return t

    def t_UNTIL(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'UNTIL\b'
        return t

    def t_CASE(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'CASE\b'
        return t

    def t_GOTO(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'GOTO\b'
        return t

    def t_WITH(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'WITH\b'
        return t

    def t_AND(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'AND\b'
        return t

    def t_OR(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'OR\b'
        return t

    def t_NOT(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'NOT\b'
        return t

    def t_IN(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'IN\b'
        return t

    def t_DIV(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'DIV\b'
        return t

    def t_MOD(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'MOD\b'
        return t

    def t_NIL(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'NIL\b'
        return t

    def t_ID(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'[a-z][a-z0-9]*'
        return t

    def t_FLOAT(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'[0-9]+(\.[0-9]+e(\+|\-)?[0-9]+|\.[0-9]+|e(\+|\-)?[0-9]+)\b'
        t.value = float(t.value)
        return t

    def t_INTEGER(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'[0-9]+\b'
        t.value = int(t.value)
        return t

    def t_STRING(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'\'((?:\'\'|[^\'])*)\''
        t.value = t.value[1:-1].replace('\'\'', '\'')
        return t

    # 6.1.9 - Lexical alternatives

    def t_ALT_CARET(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'@'
        t.type = '^'
        return t

    def t_ALT_LBRACKET(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'\(\.'
        t.type = '['
        return t

    def t_ALT_RBRACKET(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'\.\)'
        t.type = ']'
        return t

    def t_newline(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        r'\n+'

        self.commit_error(self.lexer)
        self.lexer.lineno += len(t.value)

    def t_eof(self, t: ply.lex.LexToken) -> ply.lex.LexToken:
        self.t_newline(t) # Commit error if need be
        if self.has_errors:
            raise LexerError()

    def t_error(self, _: ply.lex.LexToken) -> None:
        if self.last_error is not None:
            start, length = self.last_error

            if start + length == self.lexer.lexpos:
                # Error continuation
                self.last_error = start, length + 1
            else:
                self.commit_error(self.lexer)
                self.last_error = self.lexer.lexpos, 1
        else:
            # First error in the line
            self.last_error = self.lexer.lexpos, 1

        self.lexer.skip(1)

    def commit_error(self, lexer: ply.lex.Lexer) -> None:
        if self.last_error is not None:
            start, length = self.last_error

            print_error(self.file_path,
                        lexer.lexdata,
                        'Lexer failed to reconize the following characters',
                        lexer.lineno,
                        start,
                        length)

            self.has_errors = True
            self.last_error = None

def create_lexer(file_path: str) -> ply.lex.Lexer:
    return _Lexer(file_path).lexer
