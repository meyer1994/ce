import ply.yacc as yacc

from semantic import *
from lexer import tokens, literals

precedence = [
    ('left', 'OP_GE', '<', 'OP_LE', '>', 'OP_EQ', 'OP_NE'),
    ('left', '&', '|', '^'),
    ('left', '+', '-'),
    ('left', '*', '/', '%'),
    ('right', 'UMINUS')
]

start = 'comeco'


def p_empty(p):
    '''
    empty :
    '''

def p_comeco(p):
    '''
    comeco : comandos
           | empty
    '''
    if p[1] is not None:
        b = Bloco(p[1])
        b.validate()

def p_comandos(p):
    '''
    comandos : comandos comando
             | comando
    '''
    if len(p) == 3:
        p[0] = p[1] + [ p[2] ]
    else:
        p[0] = [ p[1] ]


def p_comando(p):
    '''
    comando : declaracao_variavel ';'
            | atribuicao ';'
            | operacao ';'
            | declaracao_funcao
    '''
    p[0] = p[1]
    print(p[0])

def p_declaracao_variavel(p):
    '''
    declaracao_variavel : TIPO ID '=' operacao
                        | TIPO ID
    '''
    if len(p) == 5:
        p[0] = DeclaracaoVariavel(p[1], p[2], p[4])
    else:
        p[0] = DeclaracaoVariavel(p[1], p[2])

def p_declaracao_variavel_array(p):
    '''
    declaracao_variavel : TIPO ID array
    '''
    dim = len(p[3])
    p[0] = DeclaracaoVariavel(p[1], p[2], dimensions=dim)

def p_array(p):
    '''
    array : array '[' operacao ']'
          | '[' operacao ']'
    '''
    if len(p) == 5:
        p[0] = p[1] + [ p[3] ]
    else:
        p[0] = [ p[2] ]

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



def p_atribuicao(p):
    '''
    atribuicao : ID '=' operacao
    '''
    var = Variavel(p[1])
    p[0] = Atribuicao(var, p[3])

def p_atribuicao_array(p):
    '''
    atribuicao : ID array '=' operacao
    '''
    dimensions = len(p[2])
    var = Variavel(p[1], dimensions)
    p[0] = Atribuicao(var, p[4])


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
              | while_statement
              | switch_statement
              | operacao ';'
              | atribuicao ';'
              | declaracao_variavel ';'
              | return_statement ';'
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
    for_statement : STATEMENT_FOR '(' declaracao_variavel ';' operacao ';' atribuicao ')' bloco
    '''
    declaration = p[3]
    condition = p[5]
    step = p[7]
    block = p[9]
    p[0] = StatementPara(declaration, condition, step, block)

def p_while_statement(p):
    '''
    while_statement : STATEMENT_WHILE '(' operacao ')' bloco
    '''
    p[0] = StatementEnquanto(p[3], p[5])

def p_switch_statement(p):
    '''
    switch_statement : STATEMENT_SWITCH '(' operacao ')' '{' switch_cases '}'
    '''
    p[0] = StatementCaso(p[3], p[6])

def p_switch_cases(p):
    '''
    switch_cases : switch_cases STATEMENT_CASE '(' operacao ')' bloco
                 | STATEMENT_CASE '(' operacao ')' bloco
    '''
    if len(p) == 7:
        p[0] = p[1] + [ StatementSeja(p[4], p[6]) ]
    else:
        p[0] = [ StatementSeja(p[3], p[5]) ]

def p_return_statement(p):
    '''
    return_statement : STATEMENT_RETURN operacao
    '''
    p[0] = p[2]


def p_operacao_numerica(p):
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
    left = p[1]
    op = Operations.NUMERICO
    right = p[3]
    p[0] = OperacaoBinaria(left, op, right)

def p_operacao_booleana(p):
    '''
    operacao : operacao '>' operacao
             | operacao '<' operacao
             | operacao OP_GE operacao
             | operacao OP_LE operacao
             | operacao OP_EQ operacao
             | operacao OP_NE operacao
    '''
    left = p[1]
    op = Operations.OPINIAO
    right = p[3]
    p[0] = OperacaoBinaria(left, op, right)

def p_operacao_minus(p):
    '''
    operacao : '-' operacao %prec UMINUS
    '''
    p[0] = OperacaoUnaria(Operations.NUMERICO, p[2])

def p_operacao_literal(p):
    '''
    operacao : LITERAL
    '''
    p[0] = p[1]

def p_operacao_variavel(p):
    '''
    operacao : ID
    '''
    p[0] = Variavel(p[1])

def p_operacao_variavel_array(p):
    '''
    operacao : ID array
    '''
    p[0] = Variavel(p[1], len(p[2]))

def p_operacao_parenteses(p):
    '''
    operacao : '(' operacao ')'
    '''
    p[0] = p[1]

def p_operacao_chamada_funcao(p):
    '''
    operacao : ID '(' parametros ')'
             | ID '(' ')'
    '''
    if len(p) == 5:
        p[0] = ChamadaFuncao(p[1], p[3])
    else:
        p[0] = ChamadaFuncao(p[1])

def p_parametros(p):
    '''
    parametros : parametros ',' operacao
               | operacao
    '''
    if len(p) == 4:
        p[0] = p[1] + [ p[3] ]
    else:
        p[0] = [ p[1] ]



def p_TIPO(p):
    '''
    TIPO : TIPO_NADA
         | TIPO_LETRA
         | TIPO_LETRAS
         | TIPO_CURTO
         | TIPO_MEDIO
         | TIPO_COMPRIDO
         | TIPO_FLUTUA
         | TIPO_DUPLO
         | TIPO_OPINIAO
    '''
    types = {
        'nada': Types.NADA,
        'letra': Types.LETRA,
        'letras': Types.LETRAS,
        'curto': Types.NUMERICO,
        'medio': Types.NUMERICO,
        'comprido': Types.NUMERICO,
        'flutua': Types.NUMERICO,
        'duplo': Types.NUMERICO,
        'opiniao': Types.OPINIAO
    }
    p[0] = types[p[1]]

def p_LITERAL_numerico(p):
    '''
    LITERAL : LITERAL_CURTO
            | LITERAL_FLUTUA
    '''
    p[0] = LiteralValor(p[1], Types.NUMERICO)

def p_LITERAL_letra(p):
    '''
    LITERAL : LITERAL_LETRA
    '''
    p[0] = LiteralValor(p[1], Types.LETRA)

def p_LITERAL_letras(p):
    '''
    LITERAL : LITERAL_LETRAS
    '''
    p[0] = LiteralValor(p[1], Types.LETRAS)

def p_LITERAL_concordo(p):
    '''
    LITERAL : LITERAL_CONCORDO
    '''
    p[0] = LiteralValor(True, Types.OPINIAO)

def p_LITERAL_discordo(p):
    '''
    LITERAL : LITERAL_DISCORDO
    '''
    p[0] = LiteralValor(False, Types.OPINIAO)



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
