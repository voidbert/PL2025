#!/usr/bin/env python3

import re
import sys
import ply.lex

tokens = [
    'COMMENT',
    'SELECT',
    'WHERE',
    'LIMIT',
    'LBRACE',
    'RBRACE',
    'DOT',
    'NUMLIT',
    'STRLIT',
    'VARIABLE',
    'PREDICATE'
]

def t_COMMENT(t):
    r'\#.*'
    return t

def t_SELECT(t):
    r'(?i:SELECT)'
    return t

def t_WHERE(t):
    r'(?i:WHERE)'
    return t

def t_LIMIT(t):
    r'(?i:LIMIT)'
    return t

def t_LBRACE(t):
    r'{'
    return t

def t_RBRACE(t):
    r'}'
    return t

def t_DOT(t):
    r'\.'
    return t

def t_NUMLIT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRLIT(t):
    r'"(?P<LIT>.*?)"(?:@(?P<LANG>\w{2,}))?'
    t.value = re.match(t_STRLIT.__doc__, t.value).groupdict()
    return t

def t_VARIABLE(t):
    r'\?\w+'
    return t

def t_PREDICATE(t):
    r'a|(?:\w|:)+'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t'

def t_error(t):
    print(f'Illegar character "{t.value[0]}"', file=sys.stderr)
    t.lexer.skip(1)

if __name__ == '__main__':
    lexer = ply.lex.lex()
    lexer.input(sys.stdin.read())
    for token in lexer:
        print(token)
