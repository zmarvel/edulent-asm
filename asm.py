"""edulent-asm: Assembler for the 8-bit Edulent educational CPU architecture.
Copyright (C) 2017 Zack Marvel

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import string
import abc
import sys
import itertools as it
from collections import deque

OPERATORS = ['+', '-']

OPERATOR_PREC = {
    '+': 2,
    '-': 2,
}

# 0 = L, 1 = R
LEFT = 0
RIGHT = 1
OPERATOR_ASSOC = {
    '+': LEFT,
    '-': LEFT,
}


class ParserError(Exception):
    def __init__(self, instruction, message):
        self.instruction = instruction
        self.message = message

class AssemblerError(Exception):
    def __init__(self, message):
        self.message = message

class LabelError(Exception):
    def __init__(self, label, message):
        self.label = label
        self.message = message

def is_int(s):
    if s.startswith('0x'):
        return True
    elif s.startswith('0b'):
        return True
    elif s.startswith('0o'):
        return True
    elif any(c not in string.digits for c in s):
        return False
    else:
        return True

def parse_int(s):
    if s.startswith('0x'):
        return int(s, 16)
    elif s.startswith('0b'):
        return int(s, 2)
    elif s.startswith('0o'):
        return int(s, 8)
    else:
        return int(s)

def is_expr(s):
    return any(c in OPERATORS for c in s)

def is_label(s):
    s = s.lstrip('@')
    if s[0] in string.digits:
        return False
    elif any(c not in string.ascii_lowercase and c not in string.digits for c in s):
        return False
    else:
        return True

class Token(metaclass=abc.ABCMeta):
    pass

class Expression(Token):
    def __init__(self, value):
        self.value = value

    def tokenize(self):
        pos = 0
        s = self.value
        tokens = []
        while pos < len(s):
            start = pos
            end = pos
            while end < len(s) and s[end] not in OPERATORS:
                end += 1
            tokens.append(s[start:end])
            pos = end
            if pos < len(s):
                tokens.append(s[pos:pos+1])
                pos += 1
        return tokens

    def eval(self, symbols):
        tokens = self.tokenize()
        output = deque()
        operators = []
        for tok in tokens:
            if is_label(tok):
                output.append(symbols[tok.lstrip('@')])
            elif is_int(tok):
                output.append(tok)
            elif tok in OPERATORS:
                while operators != [] and\
                      (OPERATOR_PREC[operators[-1]] > OPERATOR_PREC[tok] or\
                      (OPERATOR_PREC[operators[-1]] == OPERATOR_PREC[tok] and OPERATOR_ASSOC[tok] == LEFT)) and\
                      OPERATOR_PREC[operators[-1]] != '(':
                    output.append(operators.pop())
                operators.append(tok)
            elif tok == '(':
                operators.append(tok)
            elif tok == ')':
                while operators[-1] != '(':
                    output.append(operators.pop())
                operators.pop()
        while operators != []:
            output.append(operators.pop())

        def eval_output(tok):
            if tok == '+':
                b = eval_output(output.pop())
                a = eval_output(output.pop())
                return a + b
            elif tok == '-':
                b = eval_output(output.pop())
                a = eval_output(output.pop())
                return a - b
            elif isinstance(tok, int):
                return tok
            else:
                return parse_int(tok)

        return eval_output(output.pop())

def parse_expr(s):
    return Expression(s)

def parse(lines):
    code = []
    code_labels = {}
    data = []
    data_labels = {}
    section = 'text'
    for line in lines:
        line = line.strip().lower().split(' ')
        line = list(filter(lambda s: s != '', line))
        instr = line[0] if len(line) > 0 else ''
        dest = line[1].rstrip(',') if len(line) > 1 else None
        src = line[2] if len(line) > 2 else None
        if instr == 'mov':
            if dest.startswith('['):
                addr = parse_expr(dest.lstrip('[').rstrip(']'))
                if src == 'a': # MOV [addr], A
                    code.extend((0x21, addr))
                elif src == 'ap': # MOV [addr], AP
                    code.extend((0x23, addr))
            elif src.startswith('['):
                if src == '[ap]': # MOV A, [AP]
                    opcode = 0x14
                    code.extend((opcode,))
                else:
                    addr = parse_expr(src.lstrip('[').rstrip(']'))
                    if dest == 'a': # MOV A, [addr]
                        opcode = 0x11
                    elif dest == 'ap': # MOV AP, [addr]
                        opcode = 0x13
                    else:
                        raise ParserError(' '.join(line), 'Unrecognized src reg')
                    code.extend((opcode, addr))
            else:
                opnd = parse_expr(src.lstrip('[').rstrip(']'))
                if dest == 'a': # MOV A, opnd
                    opcode = 0x19
                elif dest == 'b': # MOV B, opnd
                    opcode = 0x1c
                elif dest == 'ap': # MOV AP, opnd
                    opcode = 0x1b
                else:
                    raise ParserError(' '.join(line), 'Unrecognized dest reg')
                code.extend((opcode, opnd))
        elif instr == 'add' or instr == 'sub':
            if src.startswith('['):
                if src == '[ap]':
                    lower = 0x4
                    imm = False
                else:
                    lower = 0x1
                    imm = True
                if instr == 'add':
                    upper = 0x3
                else: # instr == 'sub'
                    upper = 0x4
                if imm:
                    addr = parse_expr(src.lstrip('[').rstrip(']'))
                    code.extend(((upper << 4) | lower, addr))
                else:
                    code.extend(((upper << 4) | lower,))
            else:
                if instr == 'add':
                    upper = 0x3
                else:
                    upper = 0x4
                if dest == 'a':
                    lower = 0x9
                elif dest == 'ap':
                    lower = 0xb
                elif dest == 'b':
                    lower = 0xc
                else:
                    raise ParserError(' '.join(line), 'Invalid dest reg')
                opnd = parse_int(src)
                if opnd > 255:
                    raise ParserError(' '.join(line), 'Immediate too large')
                code.extend(((upper << 4) | lower, opnd))
        elif instr == 'not':
            code.append(0x50)
        elif instr == 'shr':
            code.append(0x90)
        elif instr == 'or':
            if dest == 'a':
                if src.startswith('['): # OR A, [addr]
                    opcode = 0x61
                    opnd = parse_int(src.lstrip('[').rstrip(']'))
                else: # OR A, opnd
                    opcode = 0x69
                    opnd = parse_int(src)
                code.extend((opcode, opnd))
            else:
                raise ParserError(' '.join(line), 'Invalid dest reg')
        elif instr == 'and':
            if dest == 'a':
                if src.startswith('['): # AND A, [addr]
                    opcode = 0x71
                    opnd = parse_expr(src.lstrip('[').rstrip(']'))
                else: # AND A, opnd
                    opcode = 0x79
                    opnd = parse_int(src)
                code.extend((opcode, opnd))
            else:
                raise ParserError(' '.join(line), 'Invalid dest reg')
        elif instr == 'xor':
            if dest == 'a':
                if src.startswith('['): # XOR A, [addr]
                    opcode = 0x81
                    opnd = parse_expr(src.lstrip('[').rstrip(']'))
                else: # XOR A, opnd
                    opcode = 0x89
                    opnd = parse_int(src)
                code.extend((opcode, opnd))
            else:
                raise ParserError(' '.join(line), 'Invalid dest reg')

        elif instr == 'out': # OUT [addr], A
            if not dest.startswith('['):
                raise ParserError(' '.join(line), 'OUT dest must be in IO space')
            opnd = parse_expr(dest.lstrip('[').rstrip(']'))
            code.extend((0xe0, opnd))

        elif instr == 'jmp':
            if is_int(dest):
                opnd = parse_int(dest)
            else:
                opnd = parse_expr('@' + dest)
            code.extend((0xa1, opnd))
        elif instr == 'jz':
            if is_int(dest):
                opnd = parse_int(dest)
            else:
                opnd = parse_expr('@' + dest)
            code.extend((0xa5, opnd))
        elif instr == 'jc':
            if is_int(dest):
                opnd = parse_int(dest)
            else:
                opnd = parse_expr('@' + dest)
            code.extend((0xa9, opnd))

        elif instr == 'nop':
            code.extend((0x00,))
        elif instr == 'trace':
            code.extend((0xf1,))
        elif instr == 'halt':
            code.extend((0xf0,))

        elif instr.endswith(':'):
            label = instr.rstrip(':')
            if section == 'data':
                data_labels[label] = len(data)
            elif section == 'text':
                code_labels[label] = len(code)

        elif instr == '.data':
            section = 'data'
        elif instr == '.text':
            section = 'text'

        elif instr == '.byte':
            byte = parse_int(dest)
            if byte > 255:
                raise ParserError(' '.join(line), 'Immediate too large')
            data.append(byte)

        elif instr == '':
            pass

        else:
            raise ParserError(instr, 'Unrecognized instr')

    if len(code) + len(data) > 256:
        raise AssemblerError('code + data sections exceed 256 bytes')

    symbols = {}
    for label, addr in code_labels.items():
        symbols[label] = addr
    for label, addr in data_labels.items():
        symbols[label] = len(code) + addr
    return symbols, code, data


def replace_exprs(symbols, code):
    for op in code:
        if isinstance(op, Expression):
            yield op.eval(symbols)
        else:
            yield op

def assemble(lines):
    symbols, code, data = parse(lines)
    code = bytes(it.chain(replace_exprs(symbols, code), replace_exprs(symbols, data)))
    return code

if __name__ == '__main__':
    import argparse as ap

    parser = ap.ArgumentParser(description='Edulent 8-bit assembler')
    parser.add_argument('-o', '--output', type=ap.FileType('wb'),
                        help='Output (binary) file')
    parser.add_argument('-x', '--hex', type=ap.FileType('w'),
                        help='Output (hex) file')
    parser.add_argument('input_file', type=ap.FileType('r'),
                        help='Input (assembly) file')
    args = parser.parse_args()

    code = assemble(args.input_file)
    if args.output is not None:
        args.output.write(code)
    elif args.hex is not None:
        args.hex.write(' '.join(map(lambda b: '{:02x}'.format(b), code)))
    else:
        print('error: either -o or -x is required')
        parser.print_usage()
