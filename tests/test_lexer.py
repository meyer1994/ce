from unittest import TestCase

from ce.lexer import lexer

class TestLexer(TestCase):
    def setUp(self):
        self.lexer = lexer

    def test_comment_single_line(self):
        ''' Single line comment should be ignored '''
        data = r'a; // something'
        self.lexer.input(data)
        expected = (
            ('ID', 'a'),
            (';', ';'),
        )

        for res, exp in zip(self.lexer, expected):
            self.assertEqual(res.type, exp[0])
            self.assertEqual(res.value, exp[1])

    def test_comment_multi_line(self):
        ''' Multi line comment should be ignored '''
        data = 'a; /* \n something \n */'
        self.lexer.input(data)
        expected = (
            ('ID', 'a'),
            (';', ';'),
        )

        for res, exp in zip(self.lexer, expected):
            self.assertEqual(res.type, exp[0])
            self.assertEqual(res.value, exp[1])

    def test_error(self):
        ''' Lexer error '''
        data = chr(0)
        self.lexer.input(data)
        with self.assertRaises(SyntaxError):
            next(self.lexer)

    def test_count_lines(self):
        ''' Lexer count lines '''
        data = '\n\n\n\na'
        self.lexer.input(data)
        next(self.lexer)
        self.assertEqual(self.lexer.lineno, 5)

    def test_type_letra(self):
        ''' Char declaration '''
        data = r"'a'"
        self.lexer.input(data)
        expected = (
            ('LITERAL_LETRA', 'a'),
        )

        for res, exp in zip(self.lexer, expected):
            self.assertEqual(res.type, exp[0])
            self.assertEqual(res.value, exp[1])

    def test_type_letras(self):
        ''' String declaration '''
        data = r'"some text"'
        self.lexer.input(data)
        expected = (
            ('LITERAL_LETRAS', 'some text'),
        )

        for res, exp in zip(self.lexer, expected):
            self.assertEqual(res.type, exp[0])
            self.assertEqual(res.value, exp[1])

    def test_type_flutua(self):
        ''' Float declaration '''
        data = r'1.5555'
        self.lexer.input(data)
        expected = (
            ('LITERAL_FLUTUA', 1.5555),
        )

        for res, exp in zip(self.lexer, expected):
            self.assertEqual(res.type, exp[0])
            self.assertEqual(res.value, exp[1])

    def test_type_curto(self):
        ''' String declaration '''
        data = r'1234'
        self.lexer.input(data)
        expected = (
            ('LITERAL_CURTO', 1234),
        )

        for res, exp in zip(self.lexer, expected):
            self.assertEqual(res.type, exp[0])
            self.assertEqual(res.value, exp[1])

    def test_operacao(self):
        ''' Operation '''
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

    def test_loop_para(self):
        ''' For loop '''
        data = r'para (curto i = 0; i < 2; i = i + 1) {}'
        self.lexer.input(data)
        expected = (
            ('STATEMENT_FOR', 'para'),
            ('(', '('),
            ('TIPO_CURTO', 'curto'),
            ('ID', 'i'),
            ('=', '='),
            ('LITERAL_CURTO', 0),
            (';', ';'),
            ('ID', 'i'),
            ('<', '<'),
            ('LITERAL_CURTO', 2),
            (';', ';'),
            ('ID', 'i'),
            ('=', '='),
            ('ID', 'i'),
            ('+', '+'),
            ('LITERAL_CURTO', 1),
            (')', ')'),
            ('{', '{'),
            ('}', '}')
        )
        for res, exp in zip(self.lexer, expected):
            self.assertEqual(res.type, exp[0])
            self.assertEqual(res.value, exp[1])

    def test_loop_enquanto(self):
        ''' While loop '''
        data = r'enquanto (i < 2) {}'
        self.lexer.input(data)
        expected = (
            ('STATEMENT_WHILE', 'enquanto'),
            ('(', '('),
            ('ID', 'i'),
            ('<', '<'),
            ('LITERAL_CURTO', 2),
            (')', ')'),
            ('{', '{'),
            ('}', '}')
        )
        for res, exp in zip(self.lexer, expected):
            self.assertEqual(res.type, exp[0])
            self.assertEqual(res.value, exp[1])

    def test_condition_se(self):
        ''' If/else condition '''
        data = r'se (1 > 0) {} senao {}'
        self.lexer.input(data)
        expected = (
            ('STATEMENT_IF', 'se'),
            ('(', '('),
            ('LITERAL_CURTO', 1),
            ('>', '>'),
            ('LITERAL_CURTO', 0),
            (')', ')'),
            ('{', '{'),
            ('}', '}'),
            ('STATEMENT_ELSE', 'senao'),
            ('{', '{'),
            ('}', '}')
        )
        for res, exp in zip(self.lexer, expected):
            self.assertEqual(res.type, exp[0])
            self.assertEqual(res.value, exp[1])

    def test_condition_caso(self):
        ''' Switch condition '''
        data = r'caso (a) { seja (1) {} }'
        self.lexer.input(data)
        expected = (
            ('STATEMENT_SWITCH', 'caso'),
            ('(', '('),
            ('ID', 'a'),
            (')', ')'),
            ('{', '{'),
            ('STATEMENT_CASE', 'seja'),
            ('(', '('),
            ('LITERAL_CURTO', 1),
            (')', ')'),
            ('{', '{'),
            ('}', '}'),
            ('}', '}')
        )
        for res, exp in zip(self.lexer, expected):
            self.assertEqual(res.type, exp[0])
            self.assertEqual(res.value, exp[1])

    def test_function(self):
        ''' Function '''
        data = r'curto add(curto a) { devolve a; }'
        self.lexer.input(data)
        expected = (
            ('TIPO_CURTO', 'curto'),
            ('ID', 'add'),
            ('(', '('),
            ('TIPO_CURTO', 'curto'),
            ('ID', 'a'),
            (')', ')'),
            ('{', '{'),
            ('STATEMENT_RETURN', 'devolve'),
            ('ID', 'a'),
            (';', ';'),
            ('}', '}')
        )
        for res, exp in zip(self.lexer, expected):
            self.assertEqual(res.type, exp[0])
            self.assertEqual(res.value, exp[1])
