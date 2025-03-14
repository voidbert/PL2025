#!/usr/bin/env python3

import json
import math
import re
import sys
import ply.lex
import ply.yacc

# Estado

produtos = None
saldo = 0.0

# Analisador léxico

literals = ['.', ',']
tokens = ['LISTAR', 'MOEDA', 'SELECIONAR', 'SAIR', 'ID', 'VALOR']

def t_VALOR(t):
    r'1c|2c|5c|10c|20c|50c|1e|2e'
    return t

def t_ID(t):
    r'[A-Za-z][A-Za-z0-9]*'
    if t.value in {'LISTAR', 'MOEDA', 'SELECIONAR', 'SAIR'}:
        t.type = t.value
    return t

t_ignore = ' \t\r'

def t_error(t):
    raise ValueError()

# Analisador sintático

def p_comando(p):
    '''
    comando : listar
            | sair
            | selecionar
            | moeda
    '''

def p_listar(p):
    '''
    listar : LISTAR
    '''

    print(' {0: >6} | {1: <20} | {2: >10} | {3: >4}'.format('código', 'nome', 'quantidade', 'preço'))
    print(' ' +  '-' * 50)
    for produto in produtos.values():
        print(' {0: >6} | {1: <20} | {2: >10} | {3: >4}'.format(produto['cod'],
                                                                produto['nome'],
                                                                produto['quant'],
                                                                produto['preco']))

def p_sair(p):
    '''
    sair : SAIR
    '''

    global saldo

    with open(sys.argv[1], 'w', encoding='utf-8') as f:
        json.dump(list(produtos.values()), f, indent=4)

    troco_str = ', '.join(f'{m} x {n}' for m, n in fazer_troco(saldo).items())
    print('Troco:', troco_str)
    sys.exit(0)

def p_selecionar(p):
    '''
    selecionar : SELECIONAR ID
    '''

    global saldo

    cod = p[2]
    produto = produtos.get(cod)

    if not produto or produto['quant'] <= 0:
        print('Esse produto não existe')
        return

    if saldo <= produto['preco']:
        print('Saldo insuficiente')
        return

    saldo -= produto['preco']
    produto['quant'] -= 1
    print(f'Pode retirar o seu produto: {produto['nome']}')
    print(f'Saldo: {saldo:.2f}€')

def p_moeda(p):
    '''
    moeda : MOEDA lista_moeda '.'
    '''

    global saldo
    saldo += sum(valor_moeda(m) for m in p[2])
    print(f'Saldo: {saldo:.2f}€')

def p_lista_moeda(p):
    '''
    lista_moeda : VALOR
                | VALOR ',' lista_moeda
    '''
    p[0] = [p[1]]
    if len(p) > 2:
        p[0] += p[3]

def p_error(p):
    raise ValueError()

def valor_moeda(nome: str) -> float:
    return {
        '1c':  0.01,
        '2c':  0.02,
        '5c':  0.05,
        '10c': 0.10,
        '20c': 0.20,
        '50c': 0.50,
        '1e':  1.00,
        '2e':  2.00
    }[nome]

def fazer_troco(troco: float) -> dict[str, int]:
    res = {}
    for m in ['2e', '1e', '50c', '20c', '10c', '5c', '2c', '1c']:
        v = valor_moeda(m)
        while troco + 0.001 >= v: # Floating point error pain
            troco -= v
            res[m] = res.get(m, 0) + 1

    return { k: v for k,v in res.items() if v != 0 }

if __name__ == '__main__':
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        produtos_json = json.load(f)
        produtos = { p['cod']: p for p in produtos_json }

    lexer = ply.lex.lex()
    parser = ply.yacc.yacc()
    while True:
        try:
            ast = parser.parse(input('>> '))
        except ValueError:
            print('Comando inválido', file=sys.stderr)
            continue
