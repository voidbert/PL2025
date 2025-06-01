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

from dataclasses import is_dataclass, fields
import operator
from typing import Any, Callable, cast, get_args

# pylint: disable-next=wildcard-import,unused-wildcard-import
from .ast import *

def __replace_expressions(subtree: Any,
                          replacer: Callable[[Expression], Expression],
                          visited: set[int]) -> Any:

    if id(subtree) in visited:
        return subtree
    else:
        visited.add(id(subtree))

    if isinstance(subtree, tuple):
        if isinstance(subtree[0], (UnaryOperation, BinaryOperation)):
            return replacer(subtree)
        else:
            return (__replace_expressions(subtree[0], replacer, visited), subtree[1], visited)

    elif isinstance(subtree, list):
        return [__replace_expressions(element, replacer, visited) for element in subtree]

    elif is_dataclass(subtree):
        for field in fields(subtree):
            setattr(
                subtree,
                field.name,
                __replace_expressions(getattr(subtree, field.name), replacer, visited)
            )

    return subtree

def __constant_fold_expression(expression: Expression) -> Expression:
    if isinstance(expression[0], UnaryOperation):
        sub = __constant_fold_expression(expression[0].sub)

        if isinstance(sub[0], get_args(ConstantValue)):
            unary_operation: Callable[[Any], Any] = cast(Callable[[Any], Any], {
                '+': operator.pos,
                '-': operator.neg,
                'not': operator.not_,
            }[expression[0].operator])

            return (unary_operation(sub[0]), expression[1])

        return (UnaryOperation(expression[0].operator, sub), expression[1])

    elif isinstance(expression[0], BinaryOperation):
        left = __constant_fold_expression(expression[0].left)
        right = __constant_fold_expression(expression[0].right)

        if isinstance(left[0], get_args(ConstantValue)) and \
            isinstance(right[0], get_args(ConstantValue)):

            binary_operation = {
                '+': operator.add,
                '-': operator.sub,
                '*': operator.mul,
                '/': operator.truediv,
                'div': operator.floordiv,
                'mod': operator.mod,
                'and': operator.and_,
                'or': operator.or_,
                '=': operator.eq,
                '<>': operator.ne,
                '<': operator.lt,
                '>': operator.gt,
                '<=': operator.le,
                '>=': operator.ge
            }.get(expression[0].operator)

            if binary_operation is not None:
                return (binary_operation(left[0], right[0]), expression[1])

        return (BinaryOperation(expression[0].operator, left, right), expression[1])

    return expression

def __simplify_expression(expression: Expression) -> Expression:
    if isinstance(expression[0], UnaryOperation) and expression[0].operator == 'not':
        sub = __simplify_expression(expression[0].sub)

        # not (not x) -> x
        if isinstance(sub[0], UnaryOperation) and sub[0].operator == 'not':
            return sub[0].sub

        # not (x (=|<>|<|>|<=|>=) y) -> x (<>|=|>=|<=|>|<) y
        elif isinstance(sub[0], BinaryOperation) and \
            sub[0].operator in ['=', '<>', '<', '>', '<=', '>=']:

            new_operator: BinaryOperator = cast(BinaryOperator, {
                '=': '<>',
                '<>': '=',
                '<': '>=',
                '>': '<=',
                '<=': '>',
                '>=': '<'
            }[sub[0].operator])

            return (BinaryOperation(new_operator, sub[0].left, sub[0].right), expression[1])
        else:
            return (UnaryOperation(expression[0].operator, sub), expression[1])

    elif isinstance(expression[0], BinaryOperation) and expression[0].operator in ['and', 'or']:
        left = __simplify_expression(expression[0].left)
        right = __simplify_expression(expression[0].right)

        # De Morgan's Laws
        if isinstance(left[0], UnaryOperation) and left[0].operator == 'not' and \
            isinstance(right[0], UnaryOperation) and right[0].operator == 'not':

            new_operator = 'or' if expression[0].operator == 'and' else 'and'

            return (
                UnaryOperation(
                    'not',
                    (
                        BinaryOperation(new_operator, left[0].sub, right[0].sub),
                        expression[1],
                    )
                ),
                expression[1]
            )
        else:
            return (BinaryOperation(expression[0].operator, left, right), expression[1])

    return expression

def optimize_ast(program: Program) -> None:
    __replace_expressions(
        program,
        lambda e: __simplify_expression(__constant_fold_expression(e)),
        set()
    )
