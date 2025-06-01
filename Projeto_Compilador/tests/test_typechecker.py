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

from typing import Callable, Any, Dict, List, Tuple, Union

from plpc.typechecker import (
    TypeChecker,
    TypeCheckerError,
    BuiltInType,
    EnumeratedTypeConstantValue,
    TypeDefinition,
    UnaryOperation,
    BinaryOperation,
    ArrayType,
    VariableUsage,
    VariableDefinition,
    RangeType,
)

# ------------------------------------------ EASE OF USE ------------------------------------------

class DummyLexer:
    def __init__(self) -> None:
        self.lexdata = ""

    @property
    def lineno(self) -> int:
        return 0

ExpectedMapping = Dict[str, List[Tuple[Tuple[Any, ...], Union[Any, type]]]]

def successful_test() -> Callable[[Callable[[], ExpectedMapping]], Callable[[], None]]:
    def decorator(test: Callable[[], ExpectedMapping]) -> Callable[[], None]:
        def wrapper() -> None:
            tc = TypeChecker("<test-input>", DummyLexer())

            expected_map: ExpectedMapping = test()

            for method_name, test_list in expected_map.items():
                if not hasattr(tc, method_name):
                    raise AssertionError(
                        f"TypeChecker has no method '{method_name}'"
                    )
                method = getattr(tc, method_name)

                for args_tuple, expected_or_exc in test_list:
                    if not isinstance(args_tuple, tuple):
                        raise AssertionError(
                            f"In test '{test.__name__}', for method '{method_name}', "
                            f"expected args to be a tuple, got {type(args_tuple).__name__}"
                        )

                    if isinstance(expected_or_exc, type) and issubclass(expected_or_exc, Exception):
                        try:
                            _ = method(*args_tuple)
                            raise AssertionError(
                                f"In test '{test.__name__}': "
                                f"Expected {method_name}{args_tuple} to raise "
                                f"{expected_or_exc.__name__}, but it returned successfully."
                            )
                        except expected_or_exc:
                            pass
                        except Exception as other_exc:
                            raise AssertionError(
                                f"In test '{test.__name__}': Expected {method_name}{args_tuple} "
                                f"to raise {expected_or_exc.__name__}, but it raised "
                                f"{type(other_exc).__name__} instead."
                            ) from other_exc

                    else:
                        try:
                            result = method(*args_tuple)
                        except Exception as e:
                            raise AssertionError(
                                f"In test '{test.__name__}': Calling {method_name}{args_tuple} "
                                f"raised {type(e).__name__}, but expected {expected_or_exc!r}."
                            ) from e

                        if result != expected_or_exc:
                            raise AssertionError(
                                f"In test '{test.__name__}': {method_name}{args_tuple} returned "
                                f"{result!r}, but expected {expected_or_exc!r}."
                            )

        return wrapper

    return decorator

# --------------------------------------------- TESTS ---------------------------------------------

@successful_test()
def test_constant_type() -> ExpectedMapping:
    enum_const = EnumeratedTypeConstantValue(
        name="EVEN",
        value=2,
        constant_type=TypeDefinition("MyEnum", BuiltInType.INTEGER)
    )

    return {
        "get_constant_type": [
            ( (True,), BuiltInType.BOOLEAN ),
            ( (42,), BuiltInType.INTEGER ),
            ( (3.14,), BuiltInType.REAL ),
            ( ("Z",), BuiltInType.CHAR ),
            ( ("Hi",), BuiltInType.STRING ),
            ( (enum_const,), BuiltInType.INTEGER ),
            ( ([],), TypeCheckerError ),
        ],
    }

@successful_test()
def test_constant_ordinal_value() -> ExpectedMapping:
    enum_const = EnumeratedTypeConstantValue(
        name="EVEN",
        value=2,
        constant_type=TypeDefinition("MyEnum", BuiltInType.INTEGER)
    )

    return {
        "get_constant_ordinal_value": [
            ( (False,), 0 ),
            ( (True,), 1 ),
            ( (13,), 13 ),
            ( ("C",), ord("C") ),
            ( (enum_const,), 2 ),
            ( ((3.14,),), TypeCheckerError ),
        ],
    }

@successful_test()
def test_unary_operation_type() -> ExpectedMapping:
    u_int = UnaryOperation("+", ( (7, BuiltInType.INTEGER) ))
    u_real = UnaryOperation("-", ( (2.5, BuiltInType.REAL) ))
    u_bool = UnaryOperation("not", ( (False, BuiltInType.BOOLEAN) ))

    # invalid operations
    u_bad1 = UnaryOperation("+", ( (True, BuiltInType.BOOLEAN) ))
    u_bad2 = UnaryOperation("not", ( (5, BuiltInType.INTEGER) ))

    return {
        "get_unary_operation_type": [
            ( (u_int, (0,1)), BuiltInType.INTEGER ),
            ( (u_real, (0,1)), BuiltInType.REAL ),
            ( (u_bool, (0,1)), BuiltInType.BOOLEAN ),
            ( (u_bad1, (0,1)), TypeCheckerError ),
            ( (u_bad2, (0,1)), TypeCheckerError ),
        ],
    }

@successful_test()
def test_binary_operation_type() -> ExpectedMapping:
    b1 = BinaryOperation("+", (5, BuiltInType.INTEGER), (2.3, BuiltInType.REAL))
    b2 = BinaryOperation("-", (10, BuiltInType.INTEGER), (3, BuiltInType.INTEGER))
    b3 = BinaryOperation("/", (7, BuiltInType.INTEGER), (2, BuiltInType.INTEGER))
    b4 = BinaryOperation("div", (9, BuiltInType.INTEGER), (2, BuiltInType.INTEGER))
    b5 = BinaryOperation("and", (True, BuiltInType.BOOLEAN), (False, BuiltInType.BOOLEAN))
    b6 = BinaryOperation("=", (3, BuiltInType.INTEGER), (3, BuiltInType.INTEGER))

    # invalid operations
    b_bad1 = BinaryOperation("+", (3, BuiltInType.INTEGER), (True, BuiltInType.BOOLEAN))
    b_bad2 = BinaryOperation("or", (1, BuiltInType.INTEGER), (0, BuiltInType.INTEGER))
    b_bad3 = BinaryOperation("<", (1, BuiltInType.INTEGER), (2.5, BuiltInType.REAL))

    return {
        "get_binary_operation_type": [
            ( (b1, (0,1)), BuiltInType.REAL ),
            ( (b2, (0,1)), BuiltInType.INTEGER ),
            ( (b3, (0,1)), BuiltInType.REAL ),
            ( (b4, (0,1)), BuiltInType.INTEGER ),
            ( (b5, (0,1)), BuiltInType.BOOLEAN ),
            ( (b6, (0,1)), BuiltInType.BOOLEAN ),
            ( (b_bad1, (0,1)), TypeCheckerError ),
            ( (b_bad2, (0,1)), TypeCheckerError ),
            ( (b_bad3, (0,1)), TypeCheckerError ),
        ],
    }

@successful_test()
def test_can_assign() -> ExpectedMapping:
    return {
        "can_assign": [
            ( (BuiltInType.INTEGER, BuiltInType.INTEGER), True ),
            ( (BuiltInType.REAL, BuiltInType.INTEGER), True ),
            ( (BuiltInType.STRING, BuiltInType.CHAR), True ),
            ( (BuiltInType.INTEGER, BuiltInType.REAL), False ),
            ( (BuiltInType.BOOLEAN, BuiltInType.INTEGER), False ),
            ( (BuiltInType.STRING, BuiltInType.INTEGER), False ),
        ],
    }

@successful_test()
def test_type_after_indexation() -> ExpectedMapping:
    array1 = ArrayType(BuiltInType.INTEGER, [
        RangeType(start=1, end=10, subtype=BuiltInType.INTEGER)
    ])
    array2 = ArrayType(BuiltInType.REAL, [
        RangeType(start=1, end=5, subtype=BuiltInType.INTEGER),
        RangeType(start=1, end=5, subtype=BuiltInType.INTEGER)
    ])

    return {
        "type_after_indexation": [
            ( (array1, BuiltInType.INTEGER, (0,1)), BuiltInType.INTEGER ),
            ( (array2, BuiltInType.INTEGER, (0,1)), ArrayType(BuiltInType.REAL, [
                RangeType(1,5, BuiltInType.INTEGER)
            ]) ),
            ( (BuiltInType.STRING, BuiltInType.INTEGER, (0,1)), BuiltInType.CHAR ),
            ( (array1, BuiltInType.REAL, (0,1)), TypeCheckerError ),
            ( (BuiltInType.BOOLEAN, BuiltInType.INTEGER, (0,1)), TypeCheckerError ),
        ],
    }

@successful_test()
def test_fail_on_string_indexation() -> ExpectedMapping:
    var1 = VariableUsage(
        VariableDefinition("tmp", BuiltInType.STRING, False),
        BuiltInType.STRING,
        [("A", BuiltInType.CHAR),
         ("B", BuiltInType.CHAR)]
    )

    var2 = VariableUsage(
        VariableDefinition("tmp", ArrayType(BuiltInType.INTEGER, [
            RangeType(1, 5, BuiltInType.INTEGER)
        ]), False),
        ArrayType(BuiltInType.INTEGER, [RangeType(1, 5, BuiltInType.INTEGER)]),
        [(3, BuiltInType.INTEGER)]
    )

    return {
        "fail_on_string_indexation": [
            ( (var1, (0,1)), TypeCheckerError ),
            ( (var2, (0,1)), None ),
        ],
    }
