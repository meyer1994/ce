import ply.yacc as yacc

from semantic import *
from lexer import tokens, literals

context_stack = []

precedence = [
    ('left', 'OP_GE', '<', 'OP_LE', '>'),
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
    comando : declaracao_variavel ';'
            | declaracao_funcao
    '''
    print(p[1])



def p_declaracao_variavel(p):
    '''
    declaracao_variavel : TIPO ID '=' operacao
                        | TIPO ID
    '''
    if len(p) == 4:
        p[0] = DeclaracaoVariavel(p[1], p[2], p[4])
    else:
        p[0] = DeclaracaoVariavel(p[1], p[2])

def p_declaracao_funcao(p):
    '''
    declaracao_funcao : TIPO ID '(' argumentos_funcao ')' bloco
                      | TIPO ID '(' ')' bloco
    '''
    if len(p) == 7:
        p[0] = DeclaracaoFuncao(p[1], p[2], args=p[4], block=p[6])
    else:
        p[0] = DeclaracaoFuncao(p[1], p[2], block=p[6])

def p_argumentos_funcao(p):
    '''
    argumentos_funcao : argumentos_funcao ',' TIPO ID
                      | TIPO ID
    '''
    if len(p) == 3:
        p[0] = [ Argumento(p[1], p[2]) ]
    else:
        p[0] = p[1] + [ Argumento(p[3], p[4]) ]



def p_bloco(p):
    '''
    bloco : '{' statements '}'
          | '{' '}'
    '''
    if len(p) == 4:
        p[0] = Bloco(p[2])
    else:
        p[0] = Bloco()

def p_statements(p):
    '''
    statements : statements statement
               | statement
    '''
    if len(p) == 2:
        p[0] = [ p[1] ]
    else:
        p[0] = p[1] + [ p[2] ]

def p_statement(p):
    '''
    statement : if_statement
              | for_statement
              | operacao ';'
              | declaracao_variavel ';'
    '''
    p[0] = p[1]

def p_if_statement(p):
    '''
    if_statement : STATEMENT_IF '(' operacao ')' bloco
    if_statement : STATEMENT_IF '(' operacao ')' bloco STATEMENT_ELSE bloco
    '''
    if len(p) == 6:
        p[0] = StatementSe(p[3], p[5])
    else:
        p[0] = StatementSe(p[3], p[5], p[7])

def p_for_statement(p):
    '''
    for_statement : STATEMENT_FOR '(' declaracao_variavel ';' operacao ';' operacao ')' bloco
    '''
    declaration = p[3]
    condition = p[5]
    step = p[7]
    block = p[9]
    p[0] = StatementPara(declaration, condition, step, block)


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
             | operacao '>' operacao
             | operacao '<' operacao
             | operacao OP_GE operacao
             | operacao OP_LE operacao
    '''
    operations = {
        '*': Operations.MUL,
        '/': Operations.DIV,
        '%': Operations.MOD,
        '+': Operations.ADD,
        '-': Operations.SUB,
        '&': Operations.AND,
        '^': Operations.XOR,
        '|': Operations.OR,
        '<=': Operations.LE,
        '>=': Operations.GE,
        '<': Operations.LT,
        '>': Operations.GT
    }
    left = p[1]
    op = operations[p[2]]
    right = p[3]
    p[0] = OperacaoBinaria(left, op, right)

def p_operacao_minus(p):
    '''
    operacao : '-' operacao %prec UMINUS
    '''
    p[0] = OperacaoUnaria(Operations.UMINUS, p[2])

def p_operacao_literal(p):
    '''
    operacao : LITERAL
    '''
    p[0] = p[1]

def p_operacao_variavel(p):
    '''
    operacao : ID
    '''
    p[0] = p[1]

def p_operacao_parenteses(p):
    '''
    operacao : '(' operacao ')'
    '''
    p[0] = p[1]



def p_TIPO(p):
    '''
    TIPO : TIPO_CURTO
         | TIPO_FLUTUA
    '''
    types = { t.name.lower(): t for t in Types }
    typ = types[p[1]]
    p[0] = Type(typ)

def p_LITERAL_curto(p):
    '''
    LITERAL : LITERAL_CURTO
    '''
    p[0] = LiteralValor(p[1], Types.CURTO)

def p_LITERAL_flutua(p):
    '''
    LITERAL : LITERAL_FLUTUA
    '''
    p[0] = LiteralValor(p[1], Types.FLUTUA)



def p_error(p):
    print('Error at %s' % p)


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
