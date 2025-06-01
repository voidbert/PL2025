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

from typing import Callable, Dict, Tuple
import pytest

from plpc.symboltable import (
    SymbolTable,
    SymbolTableError,
    SymbolValue,
    TypeDefinition,
    BuiltInType,
    ConstantDefinition,
    CallableDefinition,
    VariableDefinition,
    LabelDefinition,
    Block,
)

# ------------------------------------------ EASE OF USE ------------------------------------------

class DummyLexer:
    def __init__(self) -> None:
        self.lexdata = ""

    @property
    def lineno(self) -> int:
        return 0

ExpectedMapping = Dict[str, Tuple[SymbolValue, int]]

_BUILTIN_SYMBOLS : ExpectedMapping = {
    "integer": (TypeDefinition("integer", BuiltInType.INTEGER), 0),
    "real": (TypeDefinition("real", BuiltInType.REAL), 0),
    "boolean": (TypeDefinition("boolean", BuiltInType.BOOLEAN), 0),
    "char": (TypeDefinition("char", BuiltInType.CHAR), 0),
    "true": (ConstantDefinition("true", True), 0),
    "false": (ConstantDefinition("false", False), 0),
    "maxint": (ConstantDefinition("maxint", 1 << 16 - 1), 0),
    "write": (CallableDefinition("write", None, None, Block([],[],[],[],[],[])), 0),
    "writeln": (CallableDefinition("writeln", None, None, Block([],[],[],[],[],[])), 0),
    "read": (CallableDefinition("read", None, None, Block([],[],[],[],[],[])), 0),
    "readln": (CallableDefinition("readln", None, None, Block([],[],[],[],[],[])), 0),
    "string": (TypeDefinition("char", BuiltInType.STRING), 0),
    "length": (CallableDefinition("length",
                                [
                                    VariableDefinition("str", BuiltInType.STRING, True)
                                ],
                                VariableDefinition(
                                    "length", BuiltInType.INTEGER, True),
                                Block([],[],[],[],[],[])), 0),
}

def successful_test() -> Callable[[Callable[[SymbolTable], ExpectedMapping]], Callable[[], None]]:
    def decorator(test: Callable[[SymbolTable], ExpectedMapping]) -> Callable[[], None]:
        def wrapper() -> None:
            st = SymbolTable("<test-input>", DummyLexer())
            expected_map = test(st)

            got_map: ExpectedMapping = {}
            for depth, scope_dict in enumerate(st.scopes):
                for name, symval in scope_dict.items():
                    got_map[name] = (symval, depth)

            assert got_map == expected_map

        return wrapper

    return decorator

# --------------------------------------------- TESTS ---------------------------------------------

# Test scope state

@successful_test()
def test_builtin_symbols_present(symtab: SymbolTable) -> ExpectedMapping:
    # pylint: disable=unused-argument
    return _BUILTIN_SYMBOLS

@successful_test()
def test_redeclare_same_scope_raises(symtab: SymbolTable) -> ExpectedMapping:
    symtab.add(TypeDefinition("MyType", BuiltInType.INTEGER), (0,0))
    with pytest.raises(SymbolTableError):
        symtab.add(TypeDefinition("MyType", BuiltInType.REAL), (0,0))

    return {
        **_BUILTIN_SYMBOLS,
        "mytype": (TypeDefinition("MyType", BuiltInType.INTEGER), 0)
    }

@successful_test()
def test_add_global_type_and_variable(symtab: SymbolTable) -> ExpectedMapping:
    symtab.add(TypeDefinition("Point", BuiltInType.INTEGER), (0, 0))
    symtab.add(VariableDefinition("x", BuiltInType.REAL, False), (0, 0))

    return {
        **_BUILTIN_SYMBOLS,
        "point": (TypeDefinition("Point", BuiltInType.INTEGER), 0),
        "x"    : (VariableDefinition("x", BuiltInType.REAL, False), 0)
    }

@successful_test()
def test_shadowing(symtab: SymbolTable) -> ExpectedMapping:
    symtab.add(VariableDefinition("a", BuiltInType.INTEGER, False), (0,0))

    symtab.new_scope()
    symtab.add(VariableDefinition("a", BuiltInType.REAL, False), (0,0))

    return {
        **_BUILTIN_SYMBOLS,
        "a": (VariableDefinition("a", BuiltInType.REAL, False), 1)
    }

@successful_test()
def test_shadow_builtin_type(symtab: SymbolTable) -> ExpectedMapping:
    orig_def, _ = symtab.query_type("integer")

    symtab.new_scope()
    symtab.add(TypeDefinition("integer", BuiltInType.REAL), (0, 0))
    inner_def, inner_is_top = symtab.query_type("integer")
    assert inner_def == TypeDefinition("integer", BuiltInType.REAL) and inner_is_top

    symtab.unstack_top_scope()
    outer_def, outer_is_top = symtab.query_type("integer")
    assert outer_def == orig_def and outer_is_top

    return _BUILTIN_SYMBOLS

@successful_test()
def test_nested_scopes(symtab: SymbolTable) -> ExpectedMapping:
    symtab.add(VariableDefinition("A", BuiltInType.CHAR, False), (0, 0))
    symtab.new_scope()
    symtab.add(VariableDefinition("B", BuiltInType.CHAR, False), (0, 0))
    symtab.new_scope()
    symtab.add(VariableDefinition("C", BuiltInType.CHAR, False), (0, 0))

    symtab.unstack_top_scope()
    symtab.unstack_top_scope()

    return {
        **_BUILTIN_SYMBOLS,
        "a": (VariableDefinition("A", BuiltInType.CHAR, False), 0)
    }

@successful_test()
def test_unstack_global_scope(symtab: SymbolTable) -> ExpectedMapping:
    symtab.unstack_top_scope()
    return {}

# Test scope test and queries

# query_label

@successful_test()
def test_query_label_positive(symtab: SymbolTable) -> ExpectedMapping:
    symtab.add(LabelDefinition(1, None), (0, 0))
    assert isinstance(symtab.query_label(1), LabelDefinition)
    return {
        **_BUILTIN_SYMBOLS,
        "1": (LabelDefinition(1, None), 0)
    }

@successful_test()
def test_query_label_wrong_kind(symtab: SymbolTable) -> ExpectedMapping:
    symtab.add(ConstantDefinition("1", 100), (0, 0))
    with pytest.raises(SymbolTableError):
        symtab.query_label(1)
    return {
        **_BUILTIN_SYMBOLS,
        "1": (ConstantDefinition("1", 100), 0)
    }

@successful_test()
def test_query_label_not_topmost(symtab: SymbolTable) -> ExpectedMapping:
    symtab.add(LabelDefinition(0, None), (0, 0))
    symtab.new_scope()
    with pytest.raises(SymbolTableError):
        symtab.query_label(0)  # not in the topmost

    return {
        **_BUILTIN_SYMBOLS,
        "0": (LabelDefinition(0, None), 0)
    }

# query_constant

@successful_test()
def test_query_constant_positive(symtab: SymbolTable) -> ExpectedMapping:
    symtab.add(ConstantDefinition("K", 3.14), (0, 0))
    result, top_scope = symtab.query_constant("K")
    assert isinstance(result, ConstantDefinition) and top_scope
    return {
        **_BUILTIN_SYMBOLS,
        "k": (ConstantDefinition("K", 3.14), 0)
    }

# query_type

@successful_test()
def test_query_type_positive(symtab: SymbolTable) -> ExpectedMapping:
    symtab.add(TypeDefinition("T1", BuiltInType.REAL), (0, 0))
    result, top_scope = symtab.query_type("T1")
    assert isinstance(result, TypeDefinition) and top_scope
    return {
        **_BUILTIN_SYMBOLS,
        "t1": (TypeDefinition("T1", BuiltInType.REAL), 0)
    }

# query_variable

@successful_test()
def test_query_variable_positive(symtab: SymbolTable) -> ExpectedMapping:
    symtab.add(VariableDefinition("var", BuiltInType.BOOLEAN, False), (0, 0))
    result, top_scope = symtab.query_variable("var")
    assert isinstance(result, VariableDefinition) and top_scope
    return {
        **_BUILTIN_SYMBOLS,
        "var": (VariableDefinition("var", BuiltInType.BOOLEAN, False), 0)
    }

# query_callable

@successful_test()
def test_query_callable_positive(symtab: SymbolTable) -> ExpectedMapping:
    call = CallableDefinition("fn1",
        [VariableDefinition("in", BuiltInType.INTEGER, True)],
        VariableDefinition("ret", BuiltInType.BOOLEAN, False),
        Block([LabelDefinition(16, None, False)],
              [ConstantDefinition("PI", 3.1415)],
              [TypeDefinition("Point", BuiltInType.REAL)],
              [VariableDefinition("xCoord", BuiltInType.INTEGER, False)],
              [],[]))

    symtab.add(call, (0, 0))
    result, top_scope = symtab.query_callable("fn1")
    assert isinstance(result, CallableDefinition) and top_scope
    return {
        **_BUILTIN_SYMBOLS,
        "fn1": (call, 0),
    }
