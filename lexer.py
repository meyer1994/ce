
import string

import ply.lex as lex

tokens = ('NUM',)

literals = string.printable

def t_NUM(t):
    r'\d+'
    val = t.value
    t.value = int(val)
    return t

t_ignore = ' \t\v\n\f'

def t_error(t):
    print('Error at line', t.lineno, 'position', t.lexpos)

lexer = lex.lex()


#
# Scripting part
#
if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(description='Lex a file')
    arg_parser.add_argument('file', metavar='F', type=str, help='File to lex')
    args = arg_parser.parse_args()

    with open(args.file, 'r') as f:
        data = f.read()
    lexer.input(data)

    for token in lexer:
        print(token)
