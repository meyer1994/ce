from unittest import TestCase

from ce.lexer import lexer

class TestLexer(TestCase):
    def setUp(self):
        self.lexer = lexer

    def test_operacao(self):
        ''' Token generation '''
        data = '1 + a;'
        self.lexer.input(data)
        expected = (
            ('LITERAL_CURTO', 1),
            ('+', '+'),
            ('ID', 'a'),
            (';', ';'),
        )

        for res, exp in zip(self.lexer, expected):
            self.assertEqual(res.type, exp[0])
            self.assertEqual(res.value, exp[1])