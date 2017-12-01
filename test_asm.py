
import unittest
import glob
import asm

class TestInstructionEncoding(unittest.TestCase):
    def test_data_instructions(self):
        prefix = 'data'
        files = list(glob.glob('asm/{}*.asm'.format(prefix)))
        self.assertNotEqual(files, [])
        for fname in files:
            with open(fname, 'r') as f:
                code = asm.assemble(f)
            with open(fname[:-3] + 'hex', 'r') as outf:
                code_hex = []
                for line in outf:
                    code_hex.extend(line.strip().split(' '))
            for i, b in enumerate(code):
                self.assertEqual(b, int(code_hex[i], 16))
            print('{} OK'.format(fname))

    def test_alu_instructions(self):
        prefix = 'alu'
        files = list(glob.glob('asm/{}*.asm'.format(prefix)))
        self.assertNotEqual(files, [])
        for fname in files:
            with open(fname, 'r') as f:
                code = asm.assemble(f)
            with open(fname[:-3] + 'hex', 'r') as outf:
                code_hex = []
                for line in outf:
                    code_hex.extend(line.strip().split(' '))
            for i, b in enumerate(code):
                self.assertEqual(b, int(code_hex[i], 16))
            print('{} OK'.format(fname))

    def test_out_instructions(self):
        prefix = 'out'
        files = list(glob.glob('asm/{}*.asm'.format(prefix)))
        self.assertNotEqual(files, [])
        for fname in files:
            with open(fname, 'r') as f:
                code = asm.assemble(f)
            with open(fname[:-3] + 'hex', 'r') as outf:
                code_hex = []
                for line in outf:
                    code_hex.extend(line.strip().split(' '))
            for i, b in enumerate(code):
                self.assertEqual(b, int(code_hex[i], 16))
            print('{} OK'.format(fname))

    def test_control_instructions(self):
        prefix = 'control'
        files = list(glob.glob('asm/{}*.asm'.format(prefix)))
        self.assertNotEqual(files, [])
        for fname in files:
            with open(fname, 'r') as f:
                code = asm.assemble(f)
            with open(fname[:-3] + 'hex', 'r') as outf:
                code_hex = []
                for line in outf:
                    code_hex.extend(line.strip().split(' '))
            for i, b in enumerate(code):
                self.assertEqual(b, int(code_hex[i], 16))
            print('{} OK'.format(fname))



