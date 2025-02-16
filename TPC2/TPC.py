#!/usr/bin/env python3

import re

from collections.abc import Iterable
from dataclasses import dataclass
from pprint import pprint
from typing import Generator

def csv_tokens(csv_str: str) -> Generator[str, None, None]:
    matches = re.findall(r'(?:()|([^"\n;][^\n;]*)|(?:"((?:[^"]|"")*)"))[\n;]', csv_str)
    for match in matches:
        valid = [ cap for cap in match if cap ]
        if valid:
            yield valid.pop().replace('""', '"')
        else:
            yield ''

@dataclass
class PieceRegister:
    name: str
    description: str
    year: int
    period: str
    composer: str
    duration: tuple[int, int, int]
    id: str

def create_dataset_structure(csv_tokens: Iterable[str]) -> dict[str, PieceRegister]:
    for _ in range(7):
        next(csv_tokens)

    ret = {}
    while True:
        try:
            name = next(csv_tokens)
        except StopIteration:
            break

        description = next(csv_tokens)
        year        = int(next(csv_tokens))
        period      = next(csv_tokens)
        composer    = next(csv_tokens)
        duration    = tuple(int(x) for x in next(csv_tokens).split(':'))
        id          = next(csv_tokens)

        ret[id] = PieceRegister(name, description, year, period, composer, duration, id)

    return ret

def ordered_composers(dataset: dict[str, PieceRegister]) -> list[str]:
    return sorted(set(p.composer for p in dataset.values()))

def period_distribution(dataset: dict[str, PieceRegister]) -> dict[str, int]:
    ret = {}
    for piece in dataset.values():
        count = ret.get(piece.period, 0)
        ret[piece.period] = count + 1

    return ret

def period_pieces(dataset: dict[str, PieceRegister]) -> dict[str, int]:
    ret = {}
    for piece in dataset.values():
        period_pieces = ret.get(piece.period, [])
        period_pieces.append(piece.name)
        ret[piece.period] = period_pieces

    for lst in ret.values():
        lst.sort()

    return ret

if __name__ == '__main__':
    with open('dataset.csv', 'r', encoding='utf-8') as f:
        dataset_str = f.read()
        if not dataset_str.endswith('\n'):
            dataset_str += '\n'
        tokens = csv_tokens(dataset_str)
        dataset_data = create_dataset_structure(tokens)

        print('Composers in alphabetical order:')
        pprint(ordered_composers(dataset_data))

        print('\n\n\nNumber of pieces every period:')
        pprint(period_distribution(dataset_data))
        print('\n\n\nTitles of piece in each period:')
        pprint(period_pieces(dataset_data))
