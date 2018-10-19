
import string

import ply.lex as lex

reserved = {
    'curto': 'TIPO_CURTO',
    'flutua': 'TIPO_FLUTUA'
}

tokens = [
    'LITERAL_CURTO',
    'LITERAL_FLUTUA',
    'ID'
] + list(reserved.values())

literals = string.printable

def t_LITERAL_FLUTUA(t):
    r'\d+\.\d+'
    valor = float(t.value)
    tipo = 'flutua'
    t.value = (tipo, valor)
    return t

def t_LITERAL_CURTO(t):
    r'\d+'
    valor = int(t.value)
    tipo = 'curto'
    t.value = (tipo, valor)
    return t

def t_ID(t):
    r'[a-zA-Z_]+[\da-zA-Z_]*'
    valor = t.value
    t.type = reserved.get(valor, 'ID')
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
