
import ply.yacc as yacc

from lexer import tokens, literals


precedence = [
    ('left', '&', '|', '^'),
    ('left', '+', '-'),
    ('left', '*', '/', '%'),
    ('right', 'UMINUS')
]


start = 'comando'

def p_comando(p):
    '''
    comando : operacao
    '''
    print(p[1])

def p_operacao(p):
    '''
    operacao : operacao '*' operacao
             | operacao '/' operacao
             | operacao '%' operacao
             | operacao '+' operacao
             | operacao '-' operacao
             | operacao '&' operacao
             | operacao '^' operacao
             | operacao '|' operacao
    '''
    operations = {
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b,
        '%': lambda a, b: a % b,
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '&': lambda a, b: a & b,
        '^': lambda a, b: a ^ b,
        '|': lambda a, b: a | b
    }
    op = p[2]
    operation = operations[op]
    a = p[1]
    b = p[3]
    p[0] = operation(a, b)

def p_operacao_minus(p):
    '''
    operacao : '-' operacao %prec UMINUS
    '''
    p[0] = -p[2]

def p_operacao_literal(p):
    '''
    operacao : NUM
    '''
    p[0] = p[1]

def p_error(p):
    print(f'Error at line {p.lineno}, position {p.lexpos}. Value "{p.value}"')

parser = yacc.yacc(debug=True)


#
# Scripting part
#
if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(description='Parse a file')
    arg_parser.add_argument('file', metavar='F', type=str, help='File to parse')
    args = arg_parser.parse_args()

    with open(args.file, 'r') as f:
        data = f.read()
    parser.parse(data)
