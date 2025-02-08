#!/usr/bin/env python3

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Generator
from sys import stdin

@dataclass
class LiteralToken:
    content: str

@dataclass
class KeywordToken:
    content: str

Token = LiteralToken | KeywordToken

def read_literal(text: str) -> str:
    ret = ''
    for c in text:
        if c.isdigit():
            ret += c
        else:
            break
    return ret

def tokenize(text: str) -> Generator[Token, None, None]:
    i = 0
    while i < len(text):
        if text[i] == '=':
            yield KeywordToken('=')
            i += 1
        elif text[i:(i + 2)].lower() == 'on':
            yield KeywordToken('on')
            i += 2
        elif text[i:(i + 3)].lower() == 'off':
            yield KeywordToken('off')
            i += 3
        else:
            literal = read_literal(text[i:])
            if literal:
                yield LiteralToken(literal)
                i += len(literal)
            else:
                i += 1

@dataclass
class EqualNode:
    pass

@dataclass
class OnNode:
    pass

@dataclass
class OffNode:
    pass

@dataclass
class NumberNode:
    content: int

Node = EqualNode | OnNode | OffNode | NumberNode

def build_ast(tokens: Iterable[Token]) -> Generator[Node, None, None]:
    for token in tokens:
        if isinstance(token, KeywordToken):
            match token.content:
                case '=':
                    yield EqualNode()
                case 'on':
                    yield OnNode()
                case 'off':
                    yield OffNode()
        elif isinstance(token, LiteralToken):
            yield NumberNode(content=int(token.content))

def interpret(ast: Iterable[Node]):
    acc = 0
    on_off = True

    for node in ast:
        if isinstance(node, EqualNode):
            print(acc)
        elif isinstance(node, OnNode):
            on_off = True
        elif isinstance(node, OffNode):
            on_off = False
        elif isinstance(node, NumberNode) and on_off:
            acc += node.content

if __name__ == '__main__':
    interpret(build_ast(tokenize(stdin.read())))
