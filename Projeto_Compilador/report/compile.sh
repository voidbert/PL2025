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

set -e
cd "$(realpath "$(dirname -- "$0")/")"

out_dir="/tmp/latex/report-pl"
mkdir -p "build" "$out_dir"
pdflatex -halt-on-error -output-directory "$out_dir" "report.tex" < /dev/null || exit 1
cp "$out_dir/report.pdf" build
