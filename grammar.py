
import ply.yacc as yacc

from lexer import tokens, literals


symbol_table = {}


precedence = [
    ('left', '&', '|', '^'),
    ('left', '+', '-'),
    ('left', '*', '/', '%'),
    ('right', 'UMINUS')
]

start = 'comandos'

def p_empty(p):
    '''
    empty :
    '''

def p_comandos(p):
    '''
    comandos : comandos comando
             | empty
    '''

def p_comando(p):
    '''
    comando : declaracao_de_variavel ';'
            | operacao ';'
    '''
    print(p[1])

def p_declaracao_de_variavel(p):
    '''
    declaracao_de_variavel : TIPO ID '=' operacao
    '''
    tipo = p[1]
    nome = p[2]
    op_tipo, op_valor = p[4]

    if tipo == 'curto':
        valor = int(op_valor)
    elif tipo == 'flutua':
        valor = float(op_valor)

    symbol_table[nome] = (tipo, valor)

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
    operacoes = {
        '*': lambda a, b: a * b,
        '/': lambda a, b: a / b,
        '%': lambda a, b: a % b,
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '&': lambda a, b: a & b,
        '^': lambda a, b: a ^ b,
        '|': lambda a, b: a | b
    }
    operacao = operacoes[p[2]]
    a_tipo, a_valor = p[1]
    b_tipo, b_valor = p[3]

    if 'flutua' in (a_tipo, b_tipo):
        tipo = 'flutua'
    else:
        tipo = 'curto'

    valor = operacao(a_valor, b_valor)
    p[0] = (tipo, valor)

def p_operacao_minus(p):
    '''
    operacao : '-' operacao %prec UMINUS
    '''
    tipo, valor = p[2]
    p[0] = (tipo, -valor)

def p_operacao_literal(p):
    '''
    operacao : LITERAL
    '''
    p[0] = p[1]

def p_operacao_variavel(p):
    '''
    operacao : ID
    '''
    nome = p[1]
    p[0] = symbol_table[nome]

def p_operacao_parenteses(p):
    '''
    operacao : '(' operacao ')'
    '''
    p[0] = p[2]

def p_TIPO(p):
    '''
    TIPO : TIPO_CURTO
         | TIPO_FLUTUA
    '''
    p[0] = p[1]

def p_LITERAL(p):
    '''
    LITERAL : LITERAL_CURTO
            | LITERAL_FLUTUA
    '''
    p[0] = p[1]

def p_error(p):
    print(f'Error at line {p}')

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
