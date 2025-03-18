#!/usr/bin/env python3

import sys
import ply.lex

# Analisador léxico

literals = ['+', '-', '*', '/']
tokens = ['NUMBER']

def t_NUMBER(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

t_ignore = ' \t\r'

def t_error(t):
    raise ValueError()

lexer = ply.lex.lex()

# Analisador sintático

next_token = None

def rec_expr():
    global next_token

    if next_token and next_token.type == 'NUMBER':
        first_operand = next_token.value
        next_token = lexer.token()
        return (first_operand, rec_exprCont())
    else:
        raise ValueError()

def rec_exprCont():
    global next_token

    if not next_token:
        return None
    elif next_token.type in ['+', '-', '*', '/']:
        try:
            operand = next_token.value

            next_token = lexer.token()
            operator = next_token.value

            next_token = lexer.token()

            return (operand, (operator, rec_exprCont()))
        except AttributeError:
            raise ValueError()
    else:
        raise ValueError()

def parse(expr: str):
    global next_token

    lexer.input(expr)
    next_token = lexer.token()
    return rec_expr()

# Analisador semântico

def calculate_mul_div(acc, tree):
    if tree is None:
        return acc, None

    op, (r1, r2) = tree

    if op == '*':
        acc = acc * r1
        res = calculate_mul_div(acc, r2)
        return res
    elif op == '/':
        acc = acc / r1
        res = calculate_mul_div(acc, r2)
        return res
    else:
        return (acc, (op, calculate_mul_div(r1, r2)))

def calculate_add(acc, tree):
    if tree is None:
        return acc, None

    op, (r1, r2) = tree

    if op == '+':
        acc = acc + r1
        res = calculate_add(acc, r2)
        return res
    if op == '-':
        acc = acc - r1
        res = calculate_add(acc, r2)
        return res
    else:
        return (acc, (op, calculate_add(r1, r2)))

def calculate(tree):
    acc, r = tree
    tree = calculate_mul_div(acc, r)

    acc, r = tree
    tree = calculate_add(acc, r)

    return tree[0]

if __name__ == '__main__':
    while True:
        try:
            tree = parse(input('>> '))
            res = calculate(tree)
            print(res)
        except ValueError:
            print('Expressão inválida', file=sys.stderr)
            continue
        except EOFError:
            exit()
