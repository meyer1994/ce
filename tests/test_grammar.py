from unittest import TestCase

from ce.grammar import symbol_table, parser, Node

class TestSymbolTable(TestCase):

    def test_symbol_table(self):
        ''' Symbol table is filled '''
        data = 'curto a = 1;'
        parser.parse(data)
        self.assertIn('a', symbol_table)

        expected = Node(type(0), 1)
        self.assertEqual(symbol_table['a'], expected)
