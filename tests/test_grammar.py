from unittest import TestCase

from ce.grammar import symbol_table, parser, Node

class TestSymbolTable(TestCase):

    def test_symbol_table(self):
        ''' Symbol table is filled '''
        data = 'curto a = 1;'
        parser.parse(data)
        self.assertIn('a', symbol_table)

        expected = Node(type(0), 1)
        result = symbol_table['a']
        self.assertEqual(result, expected)

    def test_operacao(self):
        ''' Math operations are performed '''
        data = 'curto a = 1 + 2;'
        parser.parse(data)
        self.assertIn('a', symbol_table)

        expected = 3
        _, result = symbol_table['a']
        self.assertEqual(result, expected)

    def test_float_truncate(self):
        ''' Floating point assigned to int variable is truncated '''
        data = 'curto a = 1 + 2.4;'
        parser.parse(data)
        self.assertIn('a', symbol_table)

        expected = 3
        _, result = symbol_table['a']
        self.assertEqual(result, expected)
