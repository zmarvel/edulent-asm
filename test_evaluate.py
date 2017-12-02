
import unittest
import asm

class TestEvaluate(unittest.TestCase):
    def test_expression0(self):
        expr = '3-2+1'
        symbols = {}
        e = asm.Expression(expr)
        assert e.eval(symbols) == 2

    def test_expression1(self):
        expr = '3-asdf+1'
        symbols = {'asdf': 2}
        e = asm.Expression(expr)
        assert e.eval(symbols) == 2
        symbols = {'asdf': 3}
        e = asm.Expression(expr)
        assert e.eval(symbols) == 1
