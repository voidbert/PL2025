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
from itertools import chain
from typing import Any, get_args

# pylint: disable-next=wildcard-import,unused-wildcard-import
from .ast import *
from .error import print_unlocalized_error
from .typechecker import TypeChecker
from .symboltable import SymbolTable

class EWVMError(Exception):
    pass

class Label:
    name: str

    def __init__(self, name: str) -> None:
        self.name = name

    @staticmethod
    def callable(call: str) -> Label:
        return Label(f'FN{call}')

    @staticmethod
    def user(call: None | CallableDefinition, name: int) -> Label:
        if call is None:
            return Label(f'USER{name}')
        else:
            return Label(f'USER{name}{call.name.lower()}')

    @staticmethod
    def system(call: None | CallableDefinition, name: int) -> Label:
        if call is None:
            return Label(f'SYS{name}')
        else:
            return Label(f'SYS{name}{call.name.lower()}')

    def __str__(self) -> str:
        return f'{self.name}:'

EWVMArgument = int | float | str | Label

class EWVMStatement:
    def __init__(self, instruction: str, *args: EWVMArgument) -> None:
        self.instruction = instruction
        self.arguments = args

    def __str__(self) -> str:
        def stringize_argument(argument: EWVMArgument) -> str:
            if isinstance(argument, int):
                return str(argument)
            elif isinstance(argument, float):
                return f'{argument:.10f}'
            elif isinstance(argument, str):
                if '"' in argument:
                    pascal_escaped = argument.replace('\'', '\'\'')
                    print_unlocalized_error(
                        f'Double quotes in string \'{pascal_escaped}\' '
                        'will be removed in EWVM output',
                        True
                    )

                ewvm_escaped = argument.replace('\n', '\\n').replace('"', '')
                return f'"{ewvm_escaped}"'
            elif isinstance(argument, Label):
                return argument.name
            else:
                raise EWVMError()

        indent = '  ' * (self.instruction != 'START')
        arguments_str = ' '.join(stringize_argument(argument) for argument in self.arguments)
        return f'{indent}{self.instruction} {arguments_str}'

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, EWVMStatement):
            return False

        return self.instruction == other.instruction and self.arguments == other.arguments

class Comment:
    content: str

    def __init__(self, content: str) -> None:
        self.content = content

    def __str__(self) -> str:
        return f'  // {self.content}'

EWVMProgram = list[Label | EWVMStatement | Comment]

def export_assembly(program: EWVMProgram) -> str:
    return '\n'.join(str(e) for e in program)

def remove_ewvm_comments(program: EWVMProgram) -> EWVMProgram:
    return [e for e in program if not isinstance(e, Comment)]

class LabelGenerator:
    def __init__(self, call: None | CallableDefinition) -> None:
        self.call = call
        self.__count = 0

    def new(self) -> Label:
        self.__count += 1
        return Label.system(self.call, self.__count)

class _EWVMCodeGenerator:
    def __init__(self) -> None:
        self.program: EWVMProgram = []
        self.label_generator = LabelGenerator(None)
        self.callable: None | CallableDefinition = None
        self.type_checker = TypeChecker('', None)

    def generate_constant_assembly(self, constant: ConstantValue) -> None:
        if isinstance(constant, (bool, int)):
            self.program.append(EWVMStatement('PUSHI', int(constant)))
        elif isinstance(constant, float):
            self.program.append(EWVMStatement('PUSHF', constant))
        elif isinstance(constant, str):
            if len(constant) == 1:
                self.program.append(EWVMStatement('PUSHI', ord(constant)))
            else:
                self.program.append(EWVMStatement('PUSHS', constant))
        elif isinstance(constant, EnumeratedTypeConstantValue):
            self.program.append(EWVMStatement('PUSHI', constant.value))

    def generate_variable_creation_assembly(self,
                                              variable_type: TypeValue,
                                              scope_offset: int) -> None:

        if isinstance(variable_type, ArrayType):
            # Determine size of array
            array_size = 1
            for index_type in variable_type.dimensions:
                start = self.type_checker.get_constant_ordinal_value(index_type.start)
                end = self.type_checker.get_constant_ordinal_value(index_type.end)
                array_size *= end - start + 1

            # Create array in heap
            self.program.append(EWVMStatement('ALLOC', array_size))

            # Initialize array with loop
            label = self.label_generator.new()

            self.program.append(EWVMStatement('PUSHI', 0))
            self.program.append(label)
            self.program.append(EWVMStatement('PUSHL', scope_offset))
            self.program.append(EWVMStatement('PUSHL', scope_offset + 1))
            self.generate_variable_creation_assembly(variable_type.subtype, scope_offset)
            self.program.append(EWVMStatement('STOREN'))
            self.program.append(EWVMStatement('PUSHI', 1))
            self.program.append(EWVMStatement('ADD'))
            self.program.append(EWVMStatement('DUP', 1))
            self.program.append(EWVMStatement('PUSHI', array_size))
            self.program.append(EWVMStatement('SUPEQ'))
            self.program.append(EWVMStatement('JZ', label))
            self.program.append(EWVMStatement('POP', 1))
        else:
            constant: ConstantValue
            if variable_type in [BuiltInType.BOOLEAN, BuiltInType.INTEGER, BuiltInType.CHAR]:
                constant = 0
            elif variable_type == BuiltInType.REAL:
                constant = 0.0
            elif variable_type == BuiltInType.STRING:
                constant = ''
            elif isinstance(variable_type, list): # EnumeratedType
                first_constant = variable_type[0].value
                assert isinstance(first_constant, EnumeratedTypeConstantValue)
                constant = first_constant.value

            self.generate_constant_assembly(constant)

    def generate_variable_usage_assembly(self, usage: VariableUsage, read_write: bool) -> None:
        if read_write and len(usage.indices) == 0:
            instruction = 'STOREL' if usage.variable.callable_scope else 'STOREG'
        else:
            instruction = 'PUSHL' if usage.variable.callable_scope else 'PUSHG'

        self.program.append(EWVMStatement(instruction, usage.variable.scope_offset))

        current_type = usage.variable.variable_type
        array_end_i = 0
        for index, index_type in usage.indices:
            if isinstance(current_type, ArrayType):
                self.generate_expression_assembly((index, index_type))
                self.program.append(EWVMStatement(
                    'PUSHI',
                    self.type_checker.get_constant_ordinal_value(current_type.dimensions[0].start))
                )
                self.program.append(EWVMStatement('SUB'))

                element_size = 1
                for range_type in current_type.dimensions[1:]:
                    start = self.type_checker.get_constant_ordinal_value(range_type.start)
                    end = self.type_checker.get_constant_ordinal_value(range_type.end)
                    element_size *= end - start + 1

                if element_size != 1:
                    self.program.append(EWVMStatement('PUSHI', element_size))
                    self.program.append(EWVMStatement('MUL'))
                self.program.append(EWVMStatement('PADD'))

                current_type = self.type_checker.type_after_indexation(
                    current_type,
                    index_type,
                    (0, 0)
                )
                array_end_i += 1
            else:
                break

        if array_end_i != 0:
            if read_write:
                self.program.append(EWVMStatement('SWAP'))
                self.program.append(EWVMStatement('STORE', 0))
            else:
                self.program.append(EWVMStatement('LOAD', 0))

        if current_type == BuiltInType.STRING and array_end_i != len(usage.indices):
            # pylint: disable-next=undefined-loop-variable
            self.generate_expression_assembly((index, index_type))
            self.program.append(EWVMStatement('PUSHI', 1))
            self.program.append(EWVMStatement('SUB'))
            self.program.append(EWVMStatement('CHARAT'))

    def generate_expression_assembly(self, expression: Expression) -> None:
        if isinstance(expression[0], get_args(ConstantValue)):
            if isinstance(expression[0], str) and \
                len(expression[0]) == 1 and \
                expression[1] == BuiltInType.STRING:

                self.program.append(EWVMStatement('PUSHS', expression[0]))
            else:
                self.generate_constant_assembly(expression[0])
        elif isinstance(expression[0], VariableUsage):
            self.generate_variable_usage_assembly(expression[0], False)
        elif isinstance(expression[0], CallableCall):
            self.generate_callable_call_assembly(expression[0])
        elif isinstance(expression[0], UnaryOperation):
            if expression[0].operator == '-':
                if expression[0].sub[1] == BuiltInType.REAL:
                    self.program.append(EWVMStatement('PUSHF', 0.0))
                else:
                    self.program.append(EWVMStatement('PUSHI', 0))

                self.generate_expression_assembly(expression[0].sub)

                self.program.append(
                    EWVMStatement('FSUB' if expression[0].sub[1] == BuiltInType.REAL else 'SUB')
                )

            elif expression[0].operator == 'not':
                self.generate_expression_assembly(expression[0].sub)
                self.program.append(EWVMStatement('NOT'))

        elif isinstance(expression[0], BinaryOperation):
            self.generate_expression_assembly(expression[0].left)
            self.generate_expression_assembly(expression[0].right)

            any_real = BuiltInType.REAL in [expression[0].left[1], expression[0].right[1]]

            instruction: str
            if expression[0].operator == '+':
                instruction = 'FADD' if expression[1] == BuiltInType.REAL else 'ADD'
            elif expression[0].operator == '-':
                instruction = 'FSUB' if expression[1] == BuiltInType.REAL else 'SUB'
            elif expression[0].operator == '*':
                instruction = 'FMUL' if expression[1] == BuiltInType.REAL else 'MUL'
            elif expression[0].operator == '/':
                instruction = 'FDIV'
            elif expression[0].operator in ['div', 'mod', 'and', 'or']:
                instruction = expression[0].operator.upper()
            elif expression[0].operator in ['=', '<>']:
                instruction = 'EQUAL'
            elif expression[0].operator == '<':
                instruction = 'FINF' if any_real else 'INF'
            elif expression[0].operator == '>':
                instruction = 'FSUB' if any_real else 'SUP'
            elif expression[0].operator == '<=':
                instruction = 'FINFEQ' if any_real else 'INFEQ'
            elif expression[0].operator == '>=':
                instruction = 'FSUPEQ' if any_real else 'SUPEQ'

            self.program.append(EWVMStatement(instruction))
            if expression[0].operator == '<>':
                self.program.append(EWVMStatement('NOT'))

    def generate_builtin_callable_assembly(self, call: CallableCall) -> None:
        name = call.callable.name.lower()

        if name in ['write', 'writeln']:
            for argument in call.arguments:
                if argument[1] == BuiltInType.BOOLEAN:
                    self.generate_constant_assembly('True')
                    self.generate_constant_assembly('False')
                    self.program.append(EWVMStatement('PUSHSP'))
                    self.program.append(EWVMStatement('PUSHI', 0))
                    self.generate_expression_assembly(argument)
                    self.program.append(EWVMStatement('SUB'))
                    self.program.append(EWVMStatement('LOADN'))
                    self.program.append(EWVMStatement('WRITES'))

                elif argument[1] == BuiltInType.INTEGER:
                    self.generate_expression_assembly(argument)
                    self.program.append(EWVMStatement('WRITEI'))

                elif argument[1] == BuiltInType.REAL:
                    self.generate_expression_assembly(argument)
                    self.program.append(EWVMStatement('WRITEF'))

                elif argument[1] in [BuiltInType.CHAR]:
                    self.generate_expression_assembly(argument)
                    self.program.append(EWVMStatement('WRITECHR'))

                elif argument[1] in [BuiltInType.STRING]:
                    self.generate_expression_assembly(argument)
                    self.program.append(EWVMStatement('WRITES'))

                elif isinstance(argument[1], list): # EnumeratedType
                    for value in reversed(argument[1]):
                        self.generate_constant_assembly(value.name)

                    self.program.append(EWVMStatement('PUSHSP'))
                    self.program.append(EWVMStatement('PUSHI', 0))
                    self.generate_expression_assembly(argument)
                    self.program.append(EWVMStatement('SUB'))
                    self.program.append(EWVMStatement('LOADN'))
                    self.program.append(EWVMStatement('WRITES'))

            if name == 'writeln':
                self.program.append(EWVMStatement('WRITELN'))

        elif name in ['readln', 'read']:
            if len(call.arguments) > 1:
                print_unlocalized_error(
                    f'{name} with multiple argunments will be split into multiple {name} calls',
                    True
                )

            for argument in call.arguments:
                self.program.append(EWVMStatement('READ'))

                if argument[1] in [BuiltInType.INTEGER, BuiltInType.BOOLEAN] or \
                    isinstance(argument[1], list): # EnumeratedType

                    self.program.append(EWVMStatement('ATOI'))
                elif argument[1] == BuiltInType.REAL:
                    self.program.append(EWVMStatement('ATOF'))
                elif argument[1] == BuiltInType.CHAR:
                    end_label = self.label_generator.new()
                    self.program.append(EWVMStatement('DUP', 2))
                    self.program.append(EWVMStatement('STRLEN'))
                    self.program.append(EWVMStatement('PUSHI', 1))
                    self.program.append(EWVMStatement('EQUAL'))
                    self.program.append(EWVMStatement('NOT'))
                    self.program.append(EWVMStatement('JZ', end_label))
                    self.program.append(EWVMStatement('ERR', 'More than one character written'))
                    self.program.append(end_label)
                    self.program.append(EWVMStatement('PUSHI', 0))
                    self.program.append(EWVMStatement('CHARAT'))

                assert isinstance(argument[0], VariableUsage)
                self.generate_variable_usage_assembly(argument[0], True)

            if name == 'readln':
                self.program.append(EWVMStatement('WRITELN'))

        elif name == 'length':
            self.generate_expression_assembly(call.arguments[0])
            self.program.append(EWVMStatement('STRLEN'))

    def generate_callable_call_assembly(self, call: CallableCall) -> None:
        if call.callable.name.lower() in SymbolTable('', None).scopes[0]:
            self.generate_builtin_callable_assembly(call)
        else:
            if call.callable.return_variable is not None:
                self.generate_variable_creation_assembly(
                    call.callable.return_variable.variable_type,
                    0
                )

            for argument in call.arguments:
                self.generate_expression_assembly(argument)

            self.program.append(EWVMStatement('PUSHA', Label.callable(call.callable.name)))
            self.program.append(EWVMStatement('CALL'))

            total_pops = len(call.callable.body.variables) + len(call.arguments)
            if total_pops > 0:
                self.program.append(EWVMStatement('POP', total_pops))

    def generate_statement_assembly(self, statement: Statement) -> None:
        # Statement label
        if statement[1] is not None:
            self.program.append(Label.user(self.callable, statement[1].name))

        # Variable assignment
        if isinstance(statement[0], AssignStatement):
            self.program.append(Comment(f'{statement[0].left.variable.name} := ...'))
            self.generate_expression_assembly(statement[0].right)
            self.generate_variable_usage_assembly(statement[0].left, True)

        # GOTO
        elif isinstance(statement[0], GotoStatement):
            self.program.append(Comment(f'GOTO {statement[0].label.name}'))
            self.program.append(EWVMStatement(
                'JUMP',
                Label.user(self.callable, statement[0].label.name)
            ))

        # Procedure call
        elif isinstance(statement[0], CallableCall):
            self.program.append(Comment(f'{statement[0].callable.name}()'))
            self.generate_callable_call_assembly(statement[0])

        # BeginEndStatement
        elif isinstance(statement[0], list):
            for s in statement[0]:
                self.generate_statement_assembly(s)

        # IF
        elif isinstance(statement[0], IfStatement):
            else_label = self.label_generator.new()
            end_label = self.label_generator.new()

            self.program.append(Comment('IF'))
            self.generate_expression_assembly(statement[0].condition)
            self.program.append(EWVMStatement('JZ', else_label))
            self.generate_statement_assembly(statement[0].when_true)
            self.program.append(EWVMStatement('JUMP', end_label))
            self.program.append(else_label)
            self.generate_statement_assembly(statement[0].when_false)
            self.program.append(end_label)

        # REPEAT
        elif isinstance(statement[0], RepeatStatement):
            start_label = self.label_generator.new()

            self.program.append(Comment('REPEAT'))
            self.program.append(start_label)
            self.generate_statement_assembly((statement[0].body, None))
            self.generate_expression_assembly(statement[0].condition)
            self.program.append(EWVMStatement('JZ', start_label))

        # WHILE
        elif isinstance(statement[0], WhileStatement):
            start_label = self.label_generator.new()
            end_label = self.label_generator.new()

            self.program.append(Comment('WHILE'))
            self.program.append(start_label)
            self.generate_expression_assembly(statement[0].condition)
            self.program.append(EWVMStatement('JZ', end_label))
            self.generate_statement_assembly(statement[0].body)
            self.program.append(EWVMStatement('JUMP', start_label))
            self.program.append(end_label)

        # FOR
        elif isinstance(statement[0], ForStatement):
            start_label = self.label_generator.new()
            end_label = self.label_generator.new()

            self.program.append(Comment('FOR'))
            self.generate_expression_assembly(statement[0].final_expression)
            self.generate_expression_assembly(statement[0].initial_expression)

            self.program.append(start_label)
            self.program.append(EWVMStatement('DUP', 1))
            self.generate_variable_usage_assembly(
                VariableUsage(statement[0].variable, statement[0].variable.variable_type, []),
                True
            )

            self.program.append(EWVMStatement('COPY', 2))
            if statement[0].direction == 'to':
                self.program.append(EWVMStatement('SUPEQ'))
            elif statement[0].direction == 'downto':
                self.program.append(EWVMStatement('INFEQ'))
            self.program.append(EWVMStatement('JZ', end_label))

            self.generate_statement_assembly(statement[0].body)

            self.program.append(EWVMStatement('PUSHI', 1))
            if statement[0].direction == 'to':
                self.program.append(EWVMStatement('ADD'))
            elif statement[0].direction == 'downto':
                self.program.append(EWVMStatement('SUB'))
            self.program.append(EWVMStatement('JUMP', start_label))

            self.program.append(EWVMStatement('JZ', start_label))
            self.program.append(end_label)
            self.program.append(EWVMStatement('POP', 2))

        # CASE
        elif isinstance(statement[0], CaseStatement):
            self.program.append(Comment('CASE'))
            self.generate_expression_assembly(statement[0].expression)

            end_label = self.label_generator.new()

            for element in statement[0].elements:
                self.program.append(EWVMStatement('PUSHI', 0))

                element_end_label = self.label_generator.new()

                for label_value in element.labels:
                    self.program.append(EWVMStatement('PUSHSP'))
                    self.program.append(EWVMStatement('LOAD', -1))
                    self.generate_constant_assembly(label_value)
                    self.program.append(EWVMStatement('EQUAL'))
                    self.program.append(EWVMStatement('OR'))

                self.program.append(EWVMStatement('JZ', element_end_label))

                # Statement body
                self.program.append(EWVMStatement('POP', 1))
                self.generate_statement_assembly(element.body)
                self.program.append(EWVMStatement('JUMP', end_label))
                self.program.append(element_end_label)

            self.program.append(EWVMStatement('POP', 1))
            self.program.append(EWVMStatement('ERR', 'Case expression did not match'))
            self.program.append(end_label)

    def generate_block_assembly(self, block: Block) -> None:
        # Block start
        if self.callable is None:
            self.program.append(EWVMStatement('START'))
        else:
            self.program.append(Label.callable(self.callable.name))

        self.label_generator = LabelGenerator(self.callable)

        if self.callable is not None:
            assert self.callable.parameters is not None # This only happens on predefined functions

            # Assign variable locations
            return_variables = \
                [self.callable.return_variable] if self.callable.return_variable else []
            pre_variables = list(chain(return_variables, self.callable.parameters))
            for i, variable in enumerate(pre_variables):
                variable.scope_offset = i - len(pre_variables)

        # Initialize variables
        for i, variable in enumerate(block.variables):
            variable.scope_offset = i

            self.program.append(Comment(f'{variable.name} initialization'))
            self.generate_variable_creation_assembly(
                variable.variable_type,
                variable.scope_offset
            )

        # Statements
        self.generate_statement_assembly((block.body, None))

        # Heap variable deletion
        for variable in reversed(block.variables):
            if isinstance(variable.variable_type, ArrayType):
                # NOTE: FREE doesn't work as intended, and this is only possible because no dynamic
                #       memory allocation is being performed
                self.program.append(Comment(f'{variable.name} finalization'))
                self.program.append(EWVMStatement('POPST'))

        # Block end
        if self.callable is None:
            self.program.append(EWVMStatement('STOP'))
        else:
            assert self.callable.parameters is not None # This only happens on predefined functions
            self.program.append(EWVMStatement('RETURN'))

    def generate_program_assembly(self, program: Program) -> EWVMProgram:
        self.callable = None
        self.generate_block_assembly(program.block)

        # Callables can only occur at the top level
        for call in program.block.callables:
            self.callable = call
            self.generate_block_assembly(call.body)

        return self.program

def generate_ewvm_code(program: Program) -> EWVMProgram:
    return _EWVMCodeGenerator().generate_program_assembly(program)
