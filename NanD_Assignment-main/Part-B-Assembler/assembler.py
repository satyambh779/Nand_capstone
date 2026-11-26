#!/usr/bin/env python3
"""Two-pass assembler for the Nand2Tetris Hack computer."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

DEST = {'': '000', 'M': '001', 'D': '010', 'MD': '011', 'A': '100', 'AM': '101', 'AD': '110', 'AMD': '111'}
JUMP = {'': '000', 'JGT': '001', 'JEQ': '010', 'JGE': '011', 'JLT': '100', 'JNE': '101', 'JLE': '110', 'JMP': '111'}
COMP = {
 '0':'0101010','1':'0111111','-1':'0111010','D':'0001100','A':'0110000','M':'1110000',
 '!D':'0001101','!A':'0110001','!M':'1110001','-D':'0001111','-A':'0110011','-M':'1110011',
 'D+1':'0011111','A+1':'0110111','M+1':'1110111','D-1':'0001110','A-1':'0110010','M-1':'1110010',
 'D+A':'0000010','D+M':'1000010','D-A':'0010011','D-M':'1010011','A-D':'0000111','M-D':'1000111',
 'D&A':'0000000','D&M':'1000000','D|A':'0010101','D|M':'1010101'
}
PREDEFINED = {'SP':0,'LCL':1,'ARG':2,'THIS':3,'THAT':4,'SCREEN':16384,'KBD':24576}
PREDEFINED.update({f'R{i}':i for i in range(16)})

class AssemblyError(Exception):
    def __init__(self, line: int, message: str):
        self.line, self.message = line, message
        super().__init__(f"Line {line}: {message}")

def clean_lines(source: str):
    """Yield (physical line number, normalized instruction) pairs."""
    for number, raw in enumerate(source.splitlines(), 1):
        line = raw.split('//', 1)[0].strip()
        if line:
            yield number, re.sub(r'\s+', '', line)

def assemble_text(source: str, k: int = 93):
    if k != 93:
        raise ValueError('This project is configured for K=93 (K mod 3 = 1).')
    lines = list(clean_lines(source))
    symbols = dict(PREDEFINED)
    rom = 0
    # Pass 1: labels.
    for line_no, line in lines:
        if line.startswith('('):
            if not line.endswith(')') or len(line) < 3:
                raise AssemblyError(line_no, f"Malformed label '{line}'")
            name = line[1:-1]
            if not re.fullmatch(r'[A-Za-z_.$:][\w.$:]*', name):
                raise AssemblyError(line_no, f"Invalid label name '{name}'")
            if name in symbols:
                raise AssemblyError(line_no, f"Duplicate or reserved label '{name}'")
            symbols[name] = rom
        else:
            rom += 1
    # Pass 2: instructions and variables.
    next_ram = 16
    machine = []
    for line_no, line in lines:
        if line.startswith('('):
            continue
        if line.startswith('@'):
            value = line[1:]
            if not value:
                raise AssemblyError(line_no, 'Missing A-instruction value')
            if value.isdigit():
                address = int(value)
            else:
                if not re.fullmatch(r'[A-Za-z_.$:][\w.$:]*', value):
                    raise AssemblyError(line_no, f"Invalid symbol '{value}'")
                if value not in symbols:
                    symbols[value] = next_ram
                    next_ram += 1
                address = symbols[value]
            if not 0 <= address <= 32767:
                raise AssemblyError(line_no, f"A-instruction value out of range: {address}")
            machine.append(f'{address:016b}')
            continue
        try:
            if line.count(';') > 1 or line.count('=') > 1:
                raise ValueError('too many separators')
            left, jump = (line.split(';') + [''])[:2] if ';' in line else (line, '')
            dest, comp = (left.split('=') if '=' in left else ('', left))
            if comp not in COMP or dest not in DEST or jump not in JUMP:
                raise ValueError('unknown comp, destination, or jump mnemonic')
            machine.append('111' + COMP[comp] + DEST[dest] + JUMP[jump])
        except ValueError as exc:
            raise AssemblyError(line_no, f"Invalid instruction '{line}': {exc}") from None
    return machine, symbols

def assemble_file(input_path: Path, output_path: Path, k: int = 93):
    source = input_path.read_text(encoding='utf-8')
    machine, symbols = assemble_text(source, k)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(machine) + ('\n' if machine else ''), encoding='utf-8')
    return symbols

def main():
    parser = argparse.ArgumentParser(description='Assemble Hack .asm source into 16-bit .hack machine code.')
    parser.add_argument('input', type=Path)
    parser.add_argument('-o', '--output', type=Path)
    parser.add_argument('--k', type=int, default=93)
    parser.add_argument('--symbols', type=Path, help='Optional path to save symbol table as JSON')
    args = parser.parse_args()
    output = args.output or args.input.with_suffix('.hack')
    try:
        symbols = assemble_file(args.input, output, args.k)
        if args.symbols:
            args.symbols.write_text(json.dumps(dict(sorted(symbols.items())), indent=2), encoding='utf-8')
        print(f'Assembled {args.input} -> {output}')
        print(f'Instructions: {sum(1 for x in output.read_text().splitlines() if x.strip())}')
        if args.symbols:
            print(f'Symbol table saved: {args.symbols}')
    except (OSError, AssemblyError, ValueError) as exc:
        print(f'Assembly error: {exc}', file=sys.stderr)
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
