import ply.yacc as yacc

from ce.lexer import tokens  # NOQA

from ce.semantic.expressions import OpBin, OpUn
from ce.semantic.values import Call, Var, Assign, Literal
from ce.semantic.declarations import DeclVariable, DeclFunction
from ce.semantic.statements import Block, If, For, While, Switch, Case

from ce.types import Types, OperationTypes
from ce.scope import Scopes


precedence = [
    ('left', 'OP_GE', '<', 'OP_LE', '>', 'OP_EQ', 'OP_NE'),
    ('left', '&', '|', '^'),
    ('left', '+', '-'),
    ('left', '*', '/', '%'),
    ('right', 'UMINUS')
]

start = 'comeco'


def p_empty(p):
    ''' empty : '''
    pass


def p_comeco(p):
    '''
    comeco : comandos
           | empty
    '''
    if p[1] is not None:
        b = Block(p[1])
        scope = Scopes()
        b.validate(scope)


def p_comandos(p):
    '''
    comandos : comandos comando
             | comando
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


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
        p[0] = DeclVariable(p[1], p[2], p[4])
    else:
        p[0] = DeclVariable(p[1], p[2])


def p_declaracao_variavel_array(p):
    ''' declaracao_variavel : TIPO ID array '''
    dim = len(p[3])
    p[0] = DeclVariable(p[1], p[2], dimensions=dim)


def p_array(p):
    '''
    array : array '[' operacao ']'
          | '[' operacao ']'
    '''
    if len(p) == 5:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[2]]


def p_declaracao_funcao(p):
    '''
    declaracao_funcao : TIPO ID '(' argumentos_funcao ')' bloco
                      | TIPO ID '(' ')' bloco
    '''
    if len(p) == 7:
        p[0] = DeclFunction(p[1], p[2], args=p[4], block=p[6])
    else:
        p[0] = DeclFunction(p[1], p[2], block=p[5])


def p_argumentos_funcao(p):
    '''
    argumentos_funcao : argumentos_funcao ',' argumento
                      | argumento
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_argumento(p):
    '''
    argumento : TIPO ID
              | TIPO ID array
    '''
    if len(p) == 3:
        p[0] = DeclVariable(p[1], p[2], dimensions=0)
    else:
        dim = len(p[3])
        p[0] = DeclVariable(p[1], p[2], dimensions=dim)


def p_atribuicao(p):
    ''' atribuicao : ID '=' operacao '''
    var = Var(p[1])
    p[0] = Assign(var, p[3])


def p_atribuicao_array(p):
    ''' atribuicao : ID array '=' operacao '''
    dimensions = len(p[2])
    var = Var(p[1], dimensions)
    p[0] = Assign(var, p[4])


def p_bloco(p):
    '''
    bloco : '{' statements '}'
          | '{' '}'
    '''
    if len(p) == 4:
        p[0] = Block(p[2])
    else:
        p[0] = Block()


def p_statements(p):
    '''
    statements : statements statement
               | statement
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]


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
        p[0] = If(p[3], p[5])
    else:
        p[0] = If(p[3], p[5], p[7])


def p_for_statement(p):
    '''
    for_statement : STATEMENT_FOR '(' declaracao_variavel ';' operacao ';' atribuicao ')' bloco
    '''
    declaration = p[3]
    condition = p[5]
    step = p[7]
    block = p[9]
    p[0] = For(declaration, condition, step, block)


def p_while_statement(p):
    ''' while_statement : STATEMENT_WHILE '(' operacao ')' bloco '''
    p[0] = While(p[3], p[5])


def p_switch_statement(p):
    '''
    switch_statement : STATEMENT_SWITCH '(' operacao ')' '{' switch_cases '}'
    '''
    p[0] = Switch(p[3], p[6])


def p_switch_cases(p):
    '''
    switch_cases : switch_cases STATEMENT_CASE '(' operacao ')' bloco
                 | STATEMENT_CASE '(' operacao ')' bloco
    '''
    if len(p) == 7:
        p[0] = p[1] + [Case(p[4], p[6])]
    else:
        p[0] = [Case(p[3], p[5])]


def p_return_statement(p):
    ''' return_statement : STATEMENT_RETURN operacao '''
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
    op = OperationTypes.NUMERIC
    right = p[3]
    p[0] = OpBin(left, op, right)


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
    op = OperationTypes.BOOLEAN
    right = p[3]
    p[0] = OpBin(left, op, right)


def p_operacao_minus(p):
    ''' operacao : '-' operacao %prec UMINUS '''
    p[0] = OpUn(OperationTypes.NUMERIC, p[2])


def p_operacao_literal(p):
    ''' operacao : LITERAL '''
    p[0] = p[1]


def p_operacao_variavel(p):
    ''' operacao : ID '''
    p[0] = Var(p[1])


def p_operacao_variavel_array(p):
    ''' operacao : ID array '''
    p[0] = Var(p[1], len(p[2]))


def p_operacao_parenteses(p):
    ''' operacao : '(' operacao ')' '''
    p[0] = p[1]


def p_operacao_chamada_funcao(p):
    '''
    operacao : ID '(' parametros ')'
             | ID '(' ')'
    '''
    if len(p) == 5:
        p[0] = Call(p[1], p[3])
    else:
        p[0] = Call(p[1])


def p_parametros(p):
    '''
    parametros : parametros ',' operacao
               | operacao
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_TIPO(p):
    '''
    TIPO : TYPE_VOID
         | TYPE_CHAR
         | TYPE_STRING
         | TYPE_SHORT
         | TYPE_INT
         | TYPE_LONG
         | TYPE_FLOAT
         | TYPE_DOUBLE
         | TYPE_BOOLEAN
    '''
    types = {
        'nada': Types.VOID,
        'letra': Types.CHAR,
        'letras': Types.STRING,
        'curto': Types.SHORT,
        'medio': Types.INT,
        'comprido': Types.LONG,
        'flutua': Types.FLOAT,
        'duplo': Types.DOUBLE,
        'opiniao': Types.BOOLEAN
    }
    p[0] = types[p[1]]


def p_LITERAL_numerico_medio(p):
    ''' LITERAL : LITERAL_INT '''
    p[0] = Literal(p[1], Types.INT)


def p_LITERAL_numerico(p):
    ''' LITERAL : LITERAL_FLOAT '''
    p[0] = Literal(p[1], Types.FLOAT)


def p_LITERAL_letra(p):
    ''' LITERAL : LITERAL_CHAR '''
    p[0] = Literal(p[1], Types.CHAR)


def p_LITERAL_letras(p):
    ''' LITERAL : LITERAL_STRING '''
    p[0] = Literal(p[1], Types.STRING)


def p_LITERAL_concordo(p):
    ''' LITERAL : LITERAL_TRUE '''
    p[0] = Literal(True, Types.BOOLEAN)


def p_LITERAL_discordo(p):
    ''' LITERAL : LITERAL_FALSE '''
    p[0] = Literal(False, Types.BOOLEAN)


def p_error(p):
    print('Error at %s' % p)


def create_parser():
    return yacc.yacc(debug=True)


#
# Scripting part
#
if __name__ == '__main__':
    import argparse
    arg_parser = argparse.ArgumentParser(description='Parse a file')
    arg_parser.add_argument('file', metavar='F', type=str, help='Parse file')
    args = arg_parser.parse_args()

    with open(args.file, 'r') as f:
        data = f.read()
        parser = create_parser()
        parser.parse(data)
