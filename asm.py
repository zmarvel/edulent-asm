
import string
import abc
import sys
import itertools as it

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

def parse_int(s):
    if s.startswith('0x'):
        return int(s, 16)
    elif s.startswith('0b'):
        return int(s, 2)
    elif s.startswith('0o'):
        return int(s, 8)
    else:
        return int(s)

class Address(metaclass=abc.ABCMeta):
    pass

class Label(Address):
    def __init__(self, symbol):
        self.tokens = self.parse_symbol(symbol)
        self.symbol = self.tokens[0]

    def parse_symbol(self, sym):
        col = 0
        if not sym.startswith('@'):
            raise LabelError(sym, "Label must start with `@'")
        col += 1
        start = col
        end = col
        sym = sym.lower()
        if col < len(sym) and sym[col] in string.digits:
            raise LabelError(sym, 'Label cannot start with a number')
        while end < len(sym) and sym[end] in string.digits + string.ascii_lowercase:
            end += 1
        col = end
        tokens = [sym[start:end]]

        start = col
        end = col
        if col < len(sym):
            if sym[col] == '+':
                end += 1
                tokens.append(sym[start:end])
                col = end
            elif sym[col] == '-':
                end += 1
                tokens.append(sym[start:end])
                col = end

        start = col
        end = col
        while end < len(sym) and sym[end] in string.digits:
            end += 1
        if start < end:
            tokens.append(sym[start:end])
            col = end

        return tokens

    def eval_tokens(self, real_addr):
        # assumes only operations are + and -
        res = real_addr
        pos = 1
        while pos < len(self.tokens):
            if self.tokens[pos] == '+':
                pos += 1
                if pos >= len(self.tokens):
                    raise LabelError(self.symbol, 'Error evaluating label arithmetic')
                res += parse_int(self.tokens[pos])
                pos += 1
            elif self.tokens[pos] == '-':
                pos += 1
                if pos >= len(self.tokens):
                    raise LabelError(self.symbol, 'Error evaluating label arithmetic')
                res -= parse_int(self.tokens[pos])
                pos += 1
        return res


class AbsoluteAddress(Address):
    def __init__(self, address):
        self.address = address

def parse_addr(s):
    s = s.lstrip('[').rstrip(']')
    if s.startswith('@'):
        return Label(s)
    else:
        return AbsoluteAddress(parse_int(s))

def parse(lines):
    code = []
    code_labels = {}
    data = []
    data_labels = {}
    section = 'text'
    for line in lines:
        line = line.strip().lower().split(' ')
        instr = line[0]
        dest = line[1].rstrip(',') if len(line) > 1 else None
        src = line[2] if len(line) > 2 else None
        if instr == 'mov':
            if dest.startswith('['):
                addr = parse_addr(dest)
                if isinstance(addr, AbsoluteAddress) and addr > 255:
                    raise ParserError(' '.join(line), 'Dest addr too large')
                if src == 'a':
                    code.extend((0x21, addr))
                elif src == 'ap':
                    code.extend((0x23, addr))
            elif src.startswith('['):
                if src == '[ap]': # MOV A, [AP]
                    opcode = 0x14
                    code.extend((opcode,))
                else:
                    addr = parse_addr(src)
                    if isinstance(addr, AbsoluteAddress) and addr.address > 255:
                        raise ParserError(' '.join(line), 'Souce addr too large')
                    if dest == 'a': # MOV A, [addr]
                        opcode = 0x11
                    elif dest == 'ap': # MOV AP, [addr]
                        opcode = 0x13
                    else:
                        raise ParserError(' '.join(line), 'Unrecognized src reg')
                    code.extend((opcode, addr))
            else:
                opnd = parse_addr(src)
                if isinstance(opnd, AbsoluteAddress) and opnd.address > 255:
                    raise ParserError(' '.join(line), 'Src addr too large')
                if dest == 'a': # MOV A, opnd
                    opcode = 0x19
                elif dest == 'b':
                    opcode = 0x1c
                elif dest == 'ap':
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
                    addr = parse_addr(src)
                    if addr > 255:
                        raise ParserError(' '.join(line), 'Souce addr too large')
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
                    opnd = parse_addr(src)
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
                    opnd = parse_addr(src)
                else: # XOR A, opnd
                    opcode = 0x89
                    opnd = parse_int(src)
                code.extend((opcode, opnd))
            else:
                raise ParserError(' '.join(line), 'Invalid dest reg')

        elif instr == 'out': # OUT [addr], A
            if not dest.startswith('['):
                raise ParserError(' '.join(line), 'OUT dest must be in IO space')
            opnd = parse_addr(dest)
            code.extend((0xe0, opnd))

        elif instr == 'jmp':
            opnd = parse_addr('@' + dest)
            code.extend((0xa1, opnd))
        elif instr == 'jz':
            opnd = parse_addr('@' + dest)
            code.extend((0xa5, opnd))
        elif instr == 'jc':
            opnd = parse_addr('@' + dest)
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
    return code_labels, code, data_labels, data


def replace_addrs(code):
    for op in code:
        if isinstance(op, AbsoluteAddress):
            yield op.address
        elif isinstance(op, Label):
            res = None
            if op.symbol in code_labels:
                yield op.eval_tokens(code_labels[op.symbol])
            elif op.symbol in data_labels:
                yield len(code) + op.eval_tokens(data_labels[op.symbol])
            else:
                raise LabelError(op.symbol, 'Label not found')
        else:
            yield op

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

    text = args.input_file
    code_labels, code, data_labels, data = parse(text)
    code = bytes(it.chain(replace_addrs(code), replace_addrs(data)))
    if args.output is not None:
        args.output.write(code)
    elif args.hex is not None:
        args.hex.write(' '.join(map(lambda b: '{:02x}'.format(b), code)))
    else:
        print('error: either -o or -x is required')
        parser.print_usage()
