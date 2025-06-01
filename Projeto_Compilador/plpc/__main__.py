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

import argparse
import sys

from .ewvm import export_assembly, generate_ewvm_code, remove_ewvm_comments
from .ewvmpeephole import apply_ewvm_peephole_optimizations
from .lexer import LexerError
from .optimizer import optimize_ast
from .parser import ParserError, create_parser

def main() -> None:
    argument_parser = argparse.ArgumentParser(description='Compile Pascal for the EWVM.')
    argument_parser.add_argument('file', nargs='?', default='-', help='path to the file to compile')
    argument_parser.add_argument('-o', default='-', help='output assembly file')
    argument_parser.add_argument('-O', action='store_true', help='optimize generated code')
    argument_parser.add_argument('-g', action='store_true', help='add debug symbols')
    args = argument_parser.parse_args()

    try:
        human_readable_filename = args.file

        if args.file == '-':
            source = sys.stdin.read()
            human_readable_filename = '<stdin>'
        else:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    source = f.read()
            except IOError:
                print(f'Failed to open source file: {args.file}', file=sys.stderr)

        parser = create_parser(human_readable_filename)
        ast = parser.parse(source)

        if args.O:
            optimize_ast(ast)

        assembly = generate_ewvm_code(ast)

        if not args.g:
            assembly = remove_ewvm_comments(assembly)

        if args.O:
            assembly = apply_ewvm_peephole_optimizations(assembly)

        assembly_text = export_assembly(assembly)

        if args.o == '-':
            print(assembly_text)
        else:
            try:
                with open(args.o, 'w', encoding='utf-8') as f:
                    f.write(assembly_text)
            except IOError:
                print(f'Failed to write to output file: {args.o}', file=sys.stderr)

    except LexerError:
        print('Lexer failed. Aborting ...', file=sys.stderr)
    except ParserError:
        print('Parser failed. Aborting ...', file=sys.stderr)

if __name__ == '__main__':
    main()
