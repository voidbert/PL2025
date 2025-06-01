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

from typing import Callable
from typing import Union
from plpc.lexer import LexerError, create_lexer

# ------------------------------------------ EASE OF USE ------------------------------------------

SimpleToken = tuple[str, Union[int | float | str]]

def successful_test(source: str) -> Callable[[Callable[[], list[SimpleToken]]], Callable[[], None]]:
    def decorator(test: Callable[[], list[SimpleToken]]) -> Callable[[], None]:
        def wrapper() -> None:
            lexer = create_lexer('<test-input>')
            lexer.input(source)

            got = [ (t.type, t.value) for t in lexer ]
            expected = test()

            assert got == expected

        return wrapper

    return decorator

def failing_test(source: str) -> Callable[[Callable[[], None]], Callable[[], None]]:
    def decorator(_: Callable[[], None]) -> Callable[[], None]:
        def wrapper() -> None:
            try:
                lexer = create_lexer('<test-input>')
                lexer.input(source)
                _ = list(lexer)
            except LexerError:
                return

            assert False

        return wrapper

    return decorator

# ------------------------------------ SINGLE TOKEN TYPE TESTS ------------------------------------

# Empty strings

@successful_test('')
def test_empty_1() -> list[SimpleToken]:
    return []

@successful_test('\n\n\r\r\t\n\r')
def test_empty_2() -> list[SimpleToken]:
    return []

# Comments

@successful_test('{}')
def test_empty_comment_1() -> list[SimpleToken]:
    return []

@successful_test('(**)')
def test_empty_comment_2() -> list[SimpleToken]:
    return []

@successful_test('(*}')
def test_empty_comment_3() -> list[SimpleToken]:
    return []

@successful_test('{*)')
def test_empty_comment_4() -> list[SimpleToken]:
    return []

@successful_test('{Hello! こんにちは}')
def test_non_empty_comment_1() -> list[SimpleToken]:
    return []

@successful_test('(*Hello! こんにちは*)')
def test_non_empty_comment_2() -> list[SimpleToken]:
    return []

@successful_test('(*Hello! こんにちは}')
def test_non_empty_comment_3() -> list[SimpleToken]:
    return []

@failing_test('{')
def test_unterminated_comment_1() -> None:
    pass

@failing_test('{{{{{')
def test_unterminated_comment_2() -> None:
    pass

@failing_test('{ Hello! こんにちは')
def test_unterminated_comment_3() -> None:
    pass

@successful_test('(*')
def test_fake_unterminated_comment_1() -> list[SimpleToken]:
    return [('(', '('), ('*', '*')]

@successful_test('(*)')
def test_fake_unterminated_comment_2() -> list[SimpleToken]:
    return [('(', '('), ('*', '*'), (')', ')')]

@failing_test('{{}')
def test_nested_comment_1() -> None:
    pass

@failing_test('{a{}')
def test_nested_comment_2() -> None:
    pass

@failing_test('{{a}')
def test_nested_comment_3() -> None:
    pass

@failing_test('{a{b}')
def test_nested_comment_4() -> None:
    pass

@failing_test('{(*}')
def test_nested_comment_5() -> None:
    pass

@failing_test('{a(*}')
def test_nested_comment_6() -> None:
    pass

@failing_test('{(*a}')
def test_nested_comment_7() -> None:
    pass

@failing_test('{a(*b}')
def test_nested_comment_8() -> None:
    pass

@failing_test('{(*{}')
def test_nested_comment_9() -> None:
    pass

@failing_test('{{(*}')
def test_nested_comment_10() -> None:
    pass

# Special Symbols

@successful_test('<>')
def test_different() -> list[SimpleToken]:
    return [('DIFFERENT', '<>')]

@successful_test('<=')
def test_le() -> list[SimpleToken]:
    return [('LE', '<=')]

@successful_test('>=')
def test_ge() -> list[SimpleToken]:
    return [('GE', '>=')]

@successful_test(':=')
def test_assign() -> list[SimpleToken]:
    return [('ASSIGN', ':=')]

@successful_test('..')
def test_range() -> list[SimpleToken]:
    return [('RANGE', '..')]

# Identifiers

@successful_test('x')
def test_simple_id() -> list[SimpleToken]:
    return [('ID', 'x')]

@successful_test('MyVar123')
def test_alphanumeric_id() -> list[SimpleToken]:
    return [('ID', 'MyVar123')]

@failing_test('_start')
def test_underscore_id() -> None:
    pass

@failing_test('hello_world')
def test_underscore_id_2() -> None:
    pass

@failing_test('résumé Δelta')
def test_unicode_ids() -> None:
    pass

# Numbers

@successful_test('42')
def test_integer() -> list[SimpleToken]:
    return [('INTEGER', 42)]

@successful_test('3.14')
def test_float() -> list[SimpleToken]:
    return [('FLOAT', 3.14)]

@successful_test('1e-5')
def test_scientific_float_1() -> list[SimpleToken]:
    return [('FLOAT', 1e-5)]

@successful_test('87.35E+8')
def test_scientific_float_2() -> list[SimpleToken]:
    return [('FLOAT', 87.35E+8)]

# Full Strings

@successful_test('\'hello\'')
def test_string() -> list[SimpleToken]:
    return [('STRING', 'hello')]

@successful_test('\'\'\'\'')
def test_single_quoted_string() -> list[SimpleToken]:
    return [('STRING', '\'')]

@successful_test('\'"A string " with " quotation "marks"\'')
def test_double_quoted_string() -> list[SimpleToken]:
    return [('STRING', '"A string " with " quotation "marks"')]

@failing_test('\'unterminated')
def test_unterminated_string() -> None:
    pass

# Lexical Alternatives

@successful_test('^')
def test_alt_caret() -> list[SimpleToken]:
    return [('^', '^')]

@successful_test('(.')
def test_alt_lbracket() -> list[SimpleToken]:
    return [('[', '(.')]

@successful_test('.)')
def test_alt_rbracket() -> list[SimpleToken]:
    return [(']', '.)')]

# ------------------------------------- COMBINATION OF TOKENS -------------------------------------

# Simple combinations

@successful_test('IFIF')
def test_double_keyword_1() -> list[SimpleToken]:
    return [('ID', 'IFIF')]

@successful_test('IFIFIF')
def test_double_keyword_2() -> list[SimpleToken]:
    return [('ID', 'IFIFIF')]

@successful_test('IF IF')
def test_double_keyword_3() -> list[SimpleToken]:
    return [('IF', 'IF'), ('IF', 'IF')]

@successful_test('If9')
def test_keyword_followed_by_digit() -> list[SimpleToken]:
    return [('ID', 'If9')]

@failing_test('9If')
def test_keyword_preceded_by_digit() -> None:
    pass

@failing_test('123variable')
def test_id_prefixed_by_digit() -> None:
    pass

@successful_test('hello world')
def test_space_separated_identifiers() -> list[SimpleToken]:
    return [('ID', 'hello'), ('ID', 'world')]

@successful_test('..:=<>()[];.,')
def test_literal_combinations() -> list[SimpleToken]:
    return [
        ('RANGE', '..'),
        ('ASSIGN', ':='),
        ('DIFFERENT', '<>'),
        ('(', '('),
        (')', ')'),
        ('[', '['),
        (']', ']'),
        (';', ';'),
        ('.', '.'),
        (',', ',')
    ]

@successful_test('a<=b>=c<>d')
def test_compound_symbols() -> list[SimpleToken]:
    return [
        ('ID', 'a'),
        ('LE', '<='),
        ('ID', 'b'),
        ('GE', '>='),
        ('ID', 'c'),
        ('DIFFERENT', '<>'),
        ('ID', 'd')
    ]

@successful_test('a := ( b [ 1 ] ) ;')
def test_spaced_literals() -> list[SimpleToken]:
    return [
        ('ID', 'a'),
        ('ASSIGN', ':='),
        ('(', '('),
        ('ID', 'b'),
        ('[', '['),
        ('INTEGER', 1),
        (']', ']'),
        (')', ')'),
        (';', ';')
    ]

@successful_test('3,14')
def test_float_comma_separated() -> list[SimpleToken]:
    return [('INTEGER', 3), (',', ','), ('INTEGER', 14)]

@successful_test('x := 42 + y; { Compute something }')
def test_combined_tokens_1() -> list[SimpleToken]:
    return [('ID', 'x'), ('ASSIGN', ':='), ('INTEGER', 42), ('+', '+'), ('ID', 'y'), (';', ';')]

@successful_test('12.3.4')
def test_combined_tokens_2() -> list[SimpleToken]:
    return [('FLOAT', 12.3), ('.', '.'), ('INTEGER', 4)]

@successful_test('@hello-world')
def test_combined_tokens_3() -> list[SimpleToken]:
    return [('^', '@'), ('ID', 'hello'), ('-', '-'), ('ID', 'world')]

@successful_test('\'section \'\'\' of three quotes\'\'')
def test_early_string_termination() -> list[SimpleToken]:
    return [
        ('STRING', 'section \''),
        ('OF', 'of'),
        ('ID', 'three'),
        ('ID', 'quotes'),
        ('STRING', '')
    ]

# Program and blocks

@successful_test('PROGRAM Test; BEGIN ENd.')
def test_program_structure() -> list[SimpleToken]:
    return [
        ('PROGRAM', 'PROGRAM'),
        ('ID', 'Test'),
        (';', ';'),
        ('BEGIN', 'BEGIN'),
        ('END', 'ENd'),
        ('.', '.')
    ]

@successful_test('ProGram tEST; begin EnD.')
def test_program_structure_insensitive() -> list[SimpleToken]:
    return [
        ('PROGRAM', 'ProGram'),
        ('ID', 'tEST'),
        (';', ';'),
        ('BEGIN', 'begin'),
        ('END', 'EnD'),
        ('.', '.')
    ]

@successful_test('PROGRAMTest')
def test_keyword_adjacent_to_id() -> list[SimpleToken]:
    return [('ID', 'PROGRAMTest')]

@successful_test('LABeL 123;')
def test_declaration_label() -> list[SimpleToken]:
    return [('LABEL', 'LABeL'), ('INTEGER', 123), (';', ';')]

@successful_test('TyPE Int=INTEGER;')
def test_declaration_type() -> list[SimpleToken]:
    return [('TYPE', 'TyPE'), ('ID', 'Int'), ('=', '='), ('ID', 'INTEGER'), (';', ';')]

@successful_test('cONST PI=3.14;')
def test_declaration_const() -> list[SimpleToken]:
    return [('CONST', 'cONST'), ('ID', 'PI'), ('=', '='), ('FLOAT', 3.14), (';', ';')]

@successful_test('VaR x:Real;')
def test_declaration_var() -> list[SimpleToken]:
    return [('VAR', 'VaR'), ('ID', 'x'), (':', ':'), ('ID', 'Real'), (';', ';')]

# Type declarations

@successful_test('ArrAY [1..10] of INTEGER;')
def test_type_array() -> list[SimpleToken]:
    return [
        ('ARRAY', 'ArrAY'),
        ('[', '['),
        ('INTEGER', 1),
        ('RANGE', '..'),
        ('INTEGER', 10),
        (']', ']'),
        ('OF', 'of'),
        ('ID', 'INTEGER'),
        (';', ';')
    ]

@successful_test('PAcKeD set OF char;')
def test_type_packed() -> list[SimpleToken]:
    return [('PACKED', 'PAcKeD'), ('SET', 'set'), ('OF', 'OF'), ('ID', 'char'), (';', ';')]

@successful_test('file OF REcorD;')
def test_type_file() -> list[SimpleToken]:
    return [('FILE', 'file'), ('OF', 'OF'), ('RECORD', 'REcorD'), (';', ';')]

# Subprograms

@successful_test('Function Foo():Integer;')
def test_subprogram_function() -> list[SimpleToken]:
    return [
        ('FUNCTION', 'Function'),
        ('ID', 'Foo'),
        ('(', '('),
        (')', ')'),
        (':', ':'),
        ('ID', 'Integer'),
        (';', ';')
    ]

@successful_test('PROCEDURE Bar();')
def test_subprogram_procedure() -> list[SimpleToken]:
    return [('PROCEDURE', 'PROCEDURE'), ('ID', 'Bar'), ('(', '('), (')', ')'), (';', ';')]

# Control flow

@successful_test('If x ThEn y ELsE z;')
def test_control_flow_if() -> list[SimpleToken]:
    return [
        ('IF', 'If'),
        ('ID', 'x'),
        ('THEN', 'ThEn'),
        ('ID', 'y'),
        ('ELSE', 'ELsE'),
        ('ID', 'z'),
        (';', ';')
    ]

@successful_test('FoR i:=1 tO 10 Do;')
def test_control_flow_for() -> list[SimpleToken]:
    return [
        ('FOR', 'FoR'),
        ('ID', 'i'),
        ('ASSIGN', ':='),
        ('INTEGER', 1),
        ('TO', 'tO'),
        ('INTEGER', 10),
        ('DO', 'Do'),
        (';', ';')
    ]

@successful_test('WhilE b do;')
def test_control_flow_while() -> list[SimpleToken]:
    return [('WHILE', 'WhilE'), ('ID', 'b'), ('DO', 'do'), (';', ';')]

@successful_test('REpeAT UNtiL c;')
def test_control_flow_repeat() -> list[SimpleToken]:
    return [('REPEAT', 'REpeAT'), ('UNTIL', 'UNtiL'), ('ID', 'c'), (';', ';')]

@successful_test('casE x OF 1: END;')
def test_control_flow_case() -> list[SimpleToken]:
    return [
        ('CASE', 'casE'),
        ('ID', 'x'),
        ('OF', 'OF'),
        ('INTEGER', 1),
        (':', ':'),
        ('END', 'END'),
        (';', ';')
    ]

@successful_test('goTo 99;')
def test_control_flow_goto() -> list[SimpleToken]:
    return [('GOTO', 'goTo'), ('INTEGER', 99), (';', ';')]

@successful_test('WitH r DO;')
def test_control_flow_with() -> list[SimpleToken]:
    return [('WITH', 'WitH'), ('ID', 'r'), ('DO', 'DO'), (';', ';')]

# Operators

@successful_test('If (x AnD y) oR NoT z thEN a DiV b MoD c in d')
def test_operator_keywords() -> list[SimpleToken]:
    return [
        ('IF', 'If'),
        ('(', '('),
        ('ID', 'x'),
        ('AND', 'AnD'),
        ('ID', 'y'),
        (')', ')'),
        ('OR', 'oR'),
        ('NOT', 'NoT'),
        ('ID', 'z'),
        ('THEN', 'thEN'),
        ('ID', 'a'),
        ('DIV', 'DiV'),
        ('ID', 'b'),
        ('MOD', 'MoD'),
        ('ID', 'c'),
        ('IN', 'in'),
        ('ID', 'd')
    ]

# Values

@successful_test('ptr := nil')
def test_nil_keyword() -> list[SimpleToken]:
    return [('ID', 'ptr'), ('ASSIGN', ':='), ('NIL', 'nil')]
