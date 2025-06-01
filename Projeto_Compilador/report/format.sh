#!/bin/sh

# Copyright 2025 Humberto Gomes, José Lopes, José Matos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

cd "$(realpath "$(dirname -- "$0")/")" || exit 1

grep_error_message() {
    sed -r "s/^([^:]*):([^:]*):.*$/\1:\2 $1/g"
}

# shellcheck disable=SC2266
{
    grep -PHn '.{101,}$' "report.tex" | grep_error_message "Column exceeds 100 characters"
    grep -PHn '\t$'      "report.tex" | grep_error_message "Use of tabs"
    grep -PHn '\s+$'     "report.tex" | grep_error_message "Trailing whitespace"
} | sort -V | tee /dev/stderr | test "$(wc -l)" = 0
