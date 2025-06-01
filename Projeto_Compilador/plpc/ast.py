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

from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
from typing import Literal

@dataclass
class Program:
    name: str
    block: Block

@dataclass
class Block:
    labels: list[LabelDefinition]
    constants: list[ConstantDefinition]
    types: list[TypeDefinition]
    variables: list[VariableDefinition]
    callables: list[CallableDefinition]
    body: BeginEndStatement

@dataclass
class LabelDefinition:
    name: int
    statement: None | Statement
    used: bool = False

@dataclass
class ConstantDefinition:
    name: str
    value: ConstantValue

@dataclass
class TypeDefinition:
    name: str
    value: TypeValue

class BuiltInType(IntEnum):
    BOOLEAN = 0
    INTEGER = 1
    REAL = 2
    CHAR = 3
    STRING = 4

EnumeratedType = list[ConstantDefinition]

@dataclass
class EnumeratedTypeConstantValue:
    name: str
    value: int
    constant_type: None | TypeDefinition

@dataclass
class RangeType:
    start: ConstantValue
    end: ConstantValue
    subtype: TypeValue

@dataclass
class ArrayType:
    subtype: TypeValue
    dimensions: list[RangeType]

ConstantValue = bool | int | float | str | EnumeratedTypeConstantValue
TypeValue = BuiltInType | EnumeratedType | RangeType | ArrayType

@dataclass
class VariableDefinition:
    name: str
    variable_type: TypeValue
    callable_scope: bool
    scope_offset: int = -1

@dataclass
class VariableUsage:
    variable: VariableDefinition
    type: TypeValue
    indices: list[Expression]

@dataclass
class CallableDefinition:
    name: str
    parameters: None | list[VariableDefinition]
    return_variable: None | VariableDefinition
    body: Block

@dataclass
class CallableCall:
    callable: CallableDefinition
    arguments: list[Expression]

BinaryOperator = Literal['+', '-', '*', '/', 'div', 'mod',
                         'and', 'or', 'in',
                         '=', '<>', '<', '>', '<=', '>=']

@dataclass
class BinaryOperation:
    operator: BinaryOperator
    left: Expression
    right: Expression

UnaryOperator = Literal['+', '-', 'not']

@dataclass
class UnaryOperation:
    operator: UnaryOperator
    sub: Expression

Expression = tuple[
    ConstantValue | VariableUsage | BinaryOperation | UnaryOperation | CallableCall,
    TypeValue
]

@dataclass
class AssignStatement:
    left: VariableUsage
    right: Expression

@dataclass
class GotoStatement:
    label: LabelDefinition

@dataclass
class IfStatement:
    condition: Expression
    when_true: Statement
    when_false: Statement

@dataclass
class CaseElement:
    labels: list[ConstantValue]
    body: Statement

@dataclass
class CaseStatement:
    expression: Expression
    elements: list[CaseElement]

@dataclass
class RepeatStatement:
    condition: Expression
    body: list[Statement]

@dataclass
class WhileStatement:
    condition: Expression
    body: Statement

@dataclass
class ForStatement:
    variable: VariableDefinition
    initial_expression: Expression
    final_expression: Expression
    direction: Literal['to', 'downto']
    body: Statement

BeginEndStatement = list['Statement']
Statement = tuple[
    AssignStatement |
    GotoStatement |
    CallableCall |
    BeginEndStatement |
    IfStatement |
    CaseStatement |
    RepeatStatement |
    WhileStatement |
    ForStatement,
    LabelDefinition | None
]
