#!/usr/bin/env python3

import itertools
import random
import re
import subprocess

def generate_expression(size: int) -> str:
    operands   = [ str(random.randrange(1, 100)) for i in range(size) ]
    operations = [ random.choice(['+', '-', '*', '/']) for i in range(size - 1) ]
    expr = ' '.join(itertools.chain(*itertools.zip_longest(operands, operations, fillvalue=' ')))
    return expr

if __name__ == '__main__':
    random.seed(0)

    expressions = []
    for size in range(1, 20):
        for _ in range(1, 10):
            expressions.append(generate_expression(size))

    expected_results = [ eval(e) for e in expressions ]

    program_input = '\n'.join(expressions)
    proc = subprocess.run(['python3', 'TPC.py'], input=program_input, capture_output=True, text=True)
    results = [ float(m) for m in re.findall(r'>> (.+)', proc.stdout) ]

    assert not proc.stderr
    assert len(results) == len(expected_results)

    for exp, res, e_res in zip(expressions, results, expected_results):
        if res != e_res:
            print(f'{exp}: got {res}, expected {e_res}')
