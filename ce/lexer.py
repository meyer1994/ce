import string

import ply.lex as lex

reserved = {
    # Types
    'nada': 'TYPE_NADA',
    'letra': 'TYPE_LETRA',
    'letras': 'TYPE_LETRAS',
    'curto': 'TYPE_CURTO',
    'medio': 'TYPE_MEDIO',
    'comprido': 'TYPE_COMPRIDO',
    'flutua': 'TYPE_FLUTUA',
    'duplo': 'TYPE_DUPLO',
    'opiniao': 'TYPE_OPINIAO',

    # Literals
    'concordo': 'LITERAL_CONCORDO',
    'discordo': 'LITERAL_DISCORDO',

    # Structures
    'se': 'STATEMENT_IF',
    'senao': 'STATEMENT_ELSE',
    'para': 'STATEMENT_FOR',
    'enquanto': 'STATEMENT_WHILE',
    'caso': 'STATEMENT_SWITCH',
    'seja': 'STATEMENT_CASE',

    # Ohters
    'devolve': 'STATEMENT_RETURN',
}

tokens = [
    'LITERAL_CURTO',
    'LITERAL_FLUTUA',
    'LITERAL_LETRA',
    'LITERAL_LETRAS',
    'ID',
    'OP_GE',
    'OP_LE',
    'OP_EQ',
    'OP_NE'
] + list(reserved.values())

literals = string.printable

t_ignore_COMMENT = r'(/\*(.|\n)*?\*/)|(//.*)'

def t_ignore_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_LITERAL_LETRA(t):
    r"'.?'"
    t.value = t.value[1]
    return t

def t_LITERAL_LETRAS(t):
    r'"[^"]*"'
    val = t.value
    t.value = str(val[1:len(val)-1])
    return t

def t_LITERAL_FLUTUA(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_LITERAL_CURTO(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_OP_GE = r'>='
t_OP_LE = r'<='
t_OP_EQ = r'=='
t_OP_NE = r'!='

def t_ID(t):
    r'[a-zA-Z_]+[\da-zA-Z_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

t_ignore = ' \t\v\f'

def t_error(t):
    raise SyntaxError('Error at line %d, position %d' % (t.lineno, t.lexpos))

lexer = lex.lex()


#
# Scripting part
#
if __name__ == '__main__':
    lex.runmain() # pragma: no cover
