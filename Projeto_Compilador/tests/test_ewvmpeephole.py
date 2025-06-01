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
# --------------------------------------------------------------------------------------------------

from plpc.ewvm import EWVMStatement, EWVMProgram
from plpc.ewvmpeephole import apply_ewvm_peephole_optimizations

def test_multiple_push_single_integer() -> None:
    before: EWVMProgram = [
        EWVMStatement('PUSHI', 0)
    ]
    expected: EWVMProgram = [
        EWVMStatement('PUSHI', 0)
    ]

    after = apply_ewvm_peephole_optimizations(before)
    assert after == expected

def test_multiple_push_single_float() -> None:
    before: EWVMProgram = [
        EWVMStatement('PUSHF', 0.0)
    ]
    expected: EWVMProgram = [
        EWVMStatement('PUSHF', 0.0)
    ]

    after = apply_ewvm_peephole_optimizations(before)
    assert after == expected

def test_multiple_push_multiple_integers_no_end() -> None:
    before: EWVMProgram = [
        EWVMStatement('PUSHI', 0),
        EWVMStatement('PUSHI', 0),
        EWVMStatement('PUSHI', 0)
    ]
    expected: EWVMProgram = [
        EWVMStatement('PUSHN', 3)
    ]

    after = apply_ewvm_peephole_optimizations(before)
    assert after == expected

def test_multiple_push_multiple_integers_end() -> None:
    before: EWVMProgram = [
        EWVMStatement('PUSHI', 0),
        EWVMStatement('PUSHI', 0),
        EWVMStatement('PUSHI', 0),
        EWVMStatement('ADD')
    ]
    expected: EWVMProgram = [
        EWVMStatement('PUSHN', 3),
        EWVMStatement('ADD')
    ]

    after = apply_ewvm_peephole_optimizations(before)
    assert after == expected

def test_multiple_push_multiple_floats_no_end() -> None:
    before: EWVMProgram = [
        EWVMStatement('PUSHF', 0.0),
        EWVMStatement('PUSHF', 0.0),
        EWVMStatement('PUSHF', 0.0),
    ]
    expected: EWVMProgram = [
        EWVMStatement('PUSHN', 3)
    ]

    after = apply_ewvm_peephole_optimizations(before)
    assert after == expected

def test_multiple_push_multiple_floats_end() -> None:
    before: EWVMProgram = [
        EWVMStatement('PUSHF', 0.0),
        EWVMStatement('PUSHF', 0.0),
        EWVMStatement('PUSHF', 0.0),
        EWVMStatement('ADD')
    ]
    expected: EWVMProgram = [
        EWVMStatement('PUSHN', 3),
        EWVMStatement('ADD')
    ]

    after = apply_ewvm_peephole_optimizations(before)
    assert after == expected

def test_multiple_push_multiple_mixed_1() -> None:
    before: EWVMProgram = [
        EWVMStatement('PUSHI', 0),
        EWVMStatement('PUSHF', 0.0),
        EWVMStatement('PUSHI', 0),
        EWVMStatement('ADD')
    ]
    expected: EWVMProgram = [
        EWVMStatement('PUSHN', 3),
        EWVMStatement('ADD')
    ]

    after = apply_ewvm_peephole_optimizations(before)
    assert after == expected

def test_multiple_push_multiple_mixed_2() -> None:
    before: EWVMProgram = [
        EWVMStatement('PUSHF', 0.0),
        EWVMStatement('PUSHI', 0),
        EWVMStatement('PUSHF', 0.0),
        EWVMStatement('ADD')
    ]
    expected: EWVMProgram = [
        EWVMStatement('PUSHN', 3),
        EWVMStatement('ADD')
    ]

    after = apply_ewvm_peephole_optimizations(before)
    assert after == expected

def test_store_push_1() -> None:
    before: EWVMProgram = [
        EWVMStatement('STOREL', 100),
        EWVMStatement('PUSHL', 100)
    ]

    expected: EWVMProgram = [
        EWVMStatement('DUP', 1),
        EWVMStatement('STOREL', 100)
    ]

    after = apply_ewvm_peephole_optimizations(before)
    assert after == expected

def test_store_push_2() -> None:
    before: EWVMProgram = [
        EWVMStatement('STOREL', 100),
        EWVMStatement('PUSHL', 101)
    ]

    expected: EWVMProgram = [
        EWVMStatement('STOREL', 100),
        EWVMStatement('PUSHL', 101)
    ]

    after = apply_ewvm_peephole_optimizations(before)
    assert after == expected

def test_store_push_3() -> None:
    before: EWVMProgram = [
        EWVMStatement('STOREL', 100),
        EWVMStatement('PUSHG', 100)
    ]

    expected: EWVMProgram = [
        EWVMStatement('STOREL', 100),
        EWVMStatement('PUSHG', 100)
    ]

    after = apply_ewvm_peephole_optimizations(before)
    assert after == expected

def test_store_push_4() -> None:
    before: EWVMProgram = [
        EWVMStatement('STOREG', 100),
        EWVMStatement('PUSHG', 100)
    ]

    expected: EWVMProgram = [
        EWVMStatement('DUP', 1),
        EWVMStatement('STOREG', 100)
    ]

    after = apply_ewvm_peephole_optimizations(before)
    assert after == expected

def test_multiplication_integer_1() -> None:
    before: EWVMProgram = [
        EWVMStatement('PUSHI', 2),
        EWVMStatement('PUSHI', 3),
        EWVMStatement('MUL')
    ]

    expected: EWVMProgram = [
        EWVMStatement('PUSHI', 2),
        EWVMStatement('PUSHI', 3),
        EWVMStatement('MUL')
    ]

    after = apply_ewvm_peephole_optimizations(before)
    assert after == expected

def test_multiplication_integer_2() -> None:
    before: EWVMProgram = [
        EWVMStatement('PUSHI', 3),
        EWVMStatement('PUSHI', 2),
        EWVMStatement('MUL')
    ]

    expected: EWVMProgram = [
        EWVMStatement('PUSHI', 3),
        EWVMStatement('DUP', 1),
        EWVMStatement('ADD')
    ]

    after = apply_ewvm_peephole_optimizations(before)
    print(after[0], after[1])
    assert after == expected

def test_multiplication_float_1() -> None:
    before: EWVMProgram = [
        EWVMStatement('PUSHI', 3),
        EWVMStatement('PUSHI', 2),
        EWVMStatement('FMUL')
    ]

    expected: EWVMProgram = [
        EWVMStatement('PUSHI', 3),
        EWVMStatement('DUP', 1),
        EWVMStatement('FADD')
    ]

    after = apply_ewvm_peephole_optimizations(before)
    print(after[0], after[1])
    assert after == expected

def test_multiplication_float_2() -> None:
    before: EWVMProgram = [
        EWVMStatement('PUSHI', 3),
        EWVMStatement('PUSHF', 2.0),
        EWVMStatement('MUL')
    ]

    expected: EWVMProgram = [
        EWVMStatement('PUSHI', 3),
        EWVMStatement('DUP', 1),
        EWVMStatement('ADD')
    ]

    after = apply_ewvm_peephole_optimizations(before)
    print(after[0], after[1])
    assert after == expected
