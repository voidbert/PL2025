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

from typing import Any, Callable
from plpc.parser import ParserError, create_parser

# ------------------------------------------ EASE OF USE ------------------------------------------

def successful_test(source: str,
                    start_production: str = 'program') -> \
                    Callable[[Callable[[], Any]], Callable[[], None]]:

    def decorator(test: Callable[[], Any]) -> Callable[[], None]:
        def wrapper() -> None:
            parser = create_parser('<test-input>', start_production)
            got = parser.parse(source)
            expected = test()

            assert got == expected

        return wrapper

    return decorator

def failing_test(source: str,
                 start_production: str = 'program-definition') -> \
                 Callable[[Callable[[], None]], Callable[[], None]]:

    def decorator(_: Callable[[], None]) -> Callable[[], None]:
        def wrapper() -> None:
            try:
                parser = create_parser('<test-input>', start_production)
                _ = parser.parse(source)
            except ParserError:
                return

            assert False

        return wrapper

    return decorator

# --------------------------------------- SINGLE RULE TESTS ---------------------------------------

@successful_test('(Hello, world)', 'program-arguments')
def test_program_definition_1() -> None:
    return None

# -------------------------------------- WHOLE PROGRAM TESTS --------------------------------------
