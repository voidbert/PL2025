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

import sys

def print_error(file_path: str,
                source: str,
                error_message: str,
                line_number: int,
                start: int,
                length: int,
                warning: bool = False) -> None:

    # Error position data
    line_start = source.rfind('\n', 0, start) + 1
    if line_start == 0:
        line_start = 0

    line_end = source.find('\n', start)
    if line_end == -1:
        line_end = len(source)

    relative_start = start - line_start
    length = min(length, line_end - start)

    # Pretty print error
    color = '\033[93m' if warning else '\033[91m'
    error_type = 'warning' if warning else 'error'
    line = source[line_start:line_end]
    error_location = f'{file_path}:{line_number}:{relative_start + 1}'
    error_underline = ' ' * relative_start + color + '^' + '~' * (length - 1) + '\033[0m'

    print(f'{error_location}: {color}{error_type}\033[0m: {error_message}', file=sys.stderr)
    print(f'{line_number: 6d} | {line}', file=sys.stderr)
    print(f'         {error_underline}\n', file=sys.stderr)

def print_unlocalized_error(error_message: str, warning: bool = False) -> None:
    color = '\033[93m' if warning else '\033[91m'
    error_type = 'warning' if warning else 'error'
    print(f'{color}{error_type}\033[0m: {error_message}', file=sys.stderr)
