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
    t.value = float(t.value)
    return t

def t_LITERAL_CURTO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_]+[\da-zA-Z_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

t_ignore = ' \t\v\n\f'

def t_error(t):
    print('Error at line', t.lineno, 'position', t.lexpos)

lexer = lex.lex()


#
# Scripting part
#
if __name__ == '__main__':
    lex.runmain()
