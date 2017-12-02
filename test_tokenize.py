
import unittest
import asm

class TestTokenize(unittest.TestCase):
    def test_expression0(self):
        expr = '3-2+1'
        e = asm.Expression(expr)
        assert e.tokenize() == ['3', '-', '2', '+', '1']

    def test_expression1(self):
        expr = '3-asdf+1'
        e = asm.Expression(expr)
        assert e.tokenize() == ['3', '-', 'asdf', '+', '1']
