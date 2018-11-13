import string

import ply.lex as lex


reserved = {
    # Types
    'nada': 'TYPE_VOID',
    'letra': 'TYPE_CHAR',
    'letras': 'TYPE_STRING',
    'curto': 'TYPE_SHORT',
    'medio': 'TYPE_INT',
    'comprido': 'TYPE_LONG',
    'flutua': 'TYPE_FLOAT',
    'duplo': 'TYPE_DOUBLE',
    'opiniao': 'TYPE_BOOLEAN',

    # Literals
    'concordo': 'LITERAL_TRUE',
    'discordo': 'LITERAL_FALSE',

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
    'LITERAL_INT',
    'LITERAL_FLOAT',
    'LITERAL_CHAR',
    'LITERAL_STRING',
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


def t_LITERAL_CHAR(t):
    r"'.?'"
    t.value = t.value[1]
    return t


def t_LITERAL_STRING(t):
    r'"[^"]*"'
    val = t.value
    t.value = str(val[1:len(val)-1])
    return t


def t_LITERAL_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t


def t_LITERAL_INT(t):
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
    lex.runmain()  # pragma: no cover
