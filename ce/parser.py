import ply.yacc as yacc

from ce.lexer import tokens  # NOQA

from ce.semantic.expressions import OpBin, OpUn
from ce.semantic.values import Call, Var, Assign, Literal
from ce.semantic.declarations import DeclVariable, DeclFunction
from ce.semantic.statements import Block, If, For, While, Switch, Case, Main, \
    Return

from ce.types import Types, OpTypes


precedence = [
    ('left', 'OP_GE', '<', 'OP_LE', '>', 'OP_EQ', 'OP_NE'),
    ('left', '&', '|', '^'),
    ('left', '+', '-'),
    ('left', '*', '/', '%'),
    ('right', 'UMINUS')
]

start = 'begin'


def p_empty(p):
    ''' empty : '''
    pass


def p_begin(p):
    '''
    begin : commands
           | empty
    '''
    if p[1] is None:
        p[0] = Main()
    else:
        p[0] = Main(p[1])


def p_commands(p):
    '''
    commands : commands command
             | command
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]


def p_command(p):
    '''
    command : var_declaration ';'
            | assign ';'
            | expression ';'
            | declaracao_funcao
    '''
    p[0] = p[1]


def p_var_declaration(p):
    '''
    var_declaration : TYPE ID '=' expression
                    | TYPE ID
    '''
    if len(p) == 5:
        p[0] = DeclVariable(p[1], p[2], p[4])
    else:
        p[0] = DeclVariable(p[1], p[2])


def p_var_declaration_array(p):
    ''' var_declaration : TYPE ID array '''
    p[0] = DeclVariable(p[1], p[2], dims=p[3])


def p_array(p):
    '''
    array : array '[' expression ']'
          | '[' expression ']'
    '''
    if len(p) == 5:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[2]]


def p_declaracao_funcao(p):
    '''
    declaracao_funcao : TYPE ID '(' argumentos_funcao ')' block
                      | TYPE ID '(' ')' block
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
    argumento : TYPE ID
              | TYPE ID array
    '''
    if len(p) == 3:
        p[0] = DeclVariable(p[1], p[2])
    else:
        p[0] = DeclVariable(p[1], p[2], dims=p[3])


def p_assign(p):
    ''' assign : ID '=' expression '''
    var = Var(p[1])
    p[0] = Assign(var, p[3])


def p_assign_array(p):
    ''' assign : ID array '=' expression '''
    dimensions = len(p[2])
    var = Var(p[1], dimensions)
    p[0] = Assign(var, p[4])


def p_block(p):
    '''
    block : '{' statements '}'
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
              | expression ';'
              | assign ';'
              | var_declaration ';'
              | return_statement ';'
    '''
    p[0] = p[1]


def p_if_statement(p):
    '''
    if_statement : IF '(' expression ')' block
    if_statement : IF '(' expression ')' block ELSE block
    '''
    if len(p) == 6:
        p[0] = If(p[3], p[5])
    else:
        p[0] = If(p[3], p[5], p[7])


def p_for_statement(p):
    '''
    for_statement : FOR '(' var_declaration ';' expression ';' assign ')' block
    '''
    p[0] = For(p[3], p[5], p[7], p[9])


def p_while_statement(p):
    ''' while_statement : WHILE '(' expression ')' block '''
    p[0] = While(p[3], p[5])


def p_switch_statement(p):
    '''
    switch_statement : SWITCH '(' expression ')' '{' switch_cases '}'
    '''
    p[0] = Switch(p[3], p[6])


def p_switch_cases(p):
    '''
    switch_cases : switch_cases CASE '(' expression ')' block
                 | CASE '(' expression ')' block
    '''
    if len(p) == 7:
        p[0] = p[1] + [Case(p[4], p[6])]
    else:
        p[0] = [Case(p[3], p[5])]


def p_return_statement(p):
    ''' return_statement : RETURN expression '''
    p[0] = Return(p[2])


def p_return_statement_empty(p):
    ''' return_statement : RETURN empty '''
    p[0] = Return()


def p_expression_numerica(p):
    '''
    expression : expression '*' expression
               | expression '/' expression
               | expression '%' expression
               | expression '+' expression
               | expression '-' expression
               | expression '&' expression
               | expression '^' expression
               | expression '|' expression
               | expression '<' expression
               | expression '>' expression
               | expression OP_GE expression
               | expression OP_LE expression
               | expression OP_EQ expression
               | expression OP_NE expression
    '''
    left = p[1]
    op = OpTypes(p[2])
    right = p[3]
    p[0] = OpBin(left, op, right)


def p_expression_minus(p):
    ''' expression : '-' expression %prec UMINUS '''
    p[0] = OpUn(OpTypes.SUB, p[2])


def p_expression_literal(p):
    ''' expression : LITERAL '''
    p[0] = p[1]


def p_expression_var(p):
    ''' expression : ID '''
    p[0] = Var(p[1])


def p_expression_array(p):
    ''' expression : ID array '''
    p[0] = Var(p[1], len(p[2]))


def p_expression_parens(p):
    ''' expression : '(' expression ')' '''
    p[0] = p[2]


def p_expression_call(p):
    '''
    expression : ID '(' parameters ')'
               | ID '(' ')'
    '''
    if len(p) == 5:
        p[0] = Call(p[1], p[3])
    else:
        p[0] = Call(p[1])


def p_parameters(p):
    '''
    parameters : parameters ',' expression
               | expression
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    else:
        p[0] = [p[1]]


def p_TYPE(p):
    '''
    TYPE : VOID
         | CHAR
         | STRING
         | SHORT
         | INT
         | LONG
         | FLOAT
         | DOUBLE
         | BOOLEAN
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


def create_parser(debug=True):
    return yacc.yacc(debug=debug)


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
