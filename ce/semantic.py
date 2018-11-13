from abc import ABC, abstractmethod

import scope
from lang_types import Types, NumericTypes, cast, OperationTypes


class Node(ABC):
    '''
    Base class for the nodes of the parse tree.
    '''
    _type = None

    @abstractmethod
    def validate(self):
        pass

    @property
    def type(self):
        return self._type


class Bloco(Node):
    def __init__(self, commands=[]):
        super(Bloco, self).__init__()
        self.commands = commands

    def validate(self):
        scope.variables.create()
        for command in self.commands:
            command.validate()
        scope.variables.pop()


class StatementSe(Node):
    def __init__(self, expression, block, else_block=None):
        super(StatementSe, self).__init__()
        self.expression = expression
        self.block = block
        self.else_block = else_block

    def validate(self):
        self.expression.validate()
        if self.expression.type != Types.BOOLEAN:
            error = self.expression.type
            raise Exception('If expression must be a boolean. Got %s' % error)
        self.block.validate()
        if self.else_block:
            self.else_block.validate()


class StatementPara(Node):
    def __init__(self, declaration, condition, step, block):
        super(StatementPara, self).__init__()
        self.declaration = declaration
        self.condition = condition
        self.step = step
        self.block = block

    def validate(self):
        self.declaration.validate()
        self.condition.validate()
        if self.condition.type != Types.BOOLEAN:
            error = self.condition.type
            raise Exception('For loop condition be boolean. Got %s' % error)
        self.step.validate()
        self.block.validate()


class StatementEnquanto(Node):
    def __init__(self, condition, block):
        super(StatementEnquanto, self).__init__()
        self.condition = condition
        self.block = block

    def validate(self):
        self.condition.validate()
        if self.condition.type != Types.BOOLEAN:
            error = self.condition.type
            raise Exception('While condition must be boolean. Got %s' % error)
        self.block.validate()


class StatementCaso(Node):
    def __init__(self, value, case_blocks=[]):
        super(StatementCaso, self).__init__()
        self.value = value
        self.case_blocks = case_blocks

    def validate(self):
        self.value.validate()
        for block in self.case_blocks:
            block.validate()


class StatementSeja(Node):
    def __init__(self, value, block):
        super(StatementSeja, self).__init__()
        self.value = value
        self.block = block

    def validate(self):
        self.value.validate()
        self.block.validate()


class DeclaracaoVariavel(Node):
    def __init__(self, _type, name, expression=None, dimensions=0):
        super(DeclaracaoVariavel, self).__init__()
        self._type = _type
        self.name = name
        self.expression = expression
        self.dimensions = dimensions

    def validate(self):
        if self.name in scope.variables.current:
            raise Exception('Variable "%s" already declared' % self.name)
        else:
            scope.variables.add(self)

        if self.expression is not None:
            self.expression.validate()
            cast(self.expression.type, self.type)


class DeclaracaoFuncao(Node):
    def __init__(self, _type, name, block, args=[]):
        super(DeclaracaoFuncao, self).__init__()
        self._type = _type
        self.name = name
        self.args = args
        self.block = block

    def validate(self):
        if self.name in scope.functions:
            raise Exception('Function %s already declared' % self.name)
        else:
            scope.functions[self.name] = self

        self.block.commands = self.args + self.block.commands
        self.block.validate()


class Variavel(Node):
    def __init__(self, name, dimensions=0):
        super(Variavel, self).__init__()
        self.name = name
        self.dimensions = dimensions

    def validate(self):
        var = scope.variables.get(self.name)
        if var is None:
            raise Exception('Variable "%s" not declared' % self.name)

        if var.dimensions < self.dimensions:
            raise Exception('Trying to access bigger array dimensions')
        self._type = var.type


class Atribuicao(Node):
    def __init__(self, var, operation):
        super(Atribuicao, self).__init__()
        self.var = var
        self.operation = operation

    def validate(self):
        self.var.validate()
        self.operation.validate()
        cast(self.var.type, self.operation.type)


class ChamadaFuncao(Node):
    def __init__(self, name, args=[]):
        super(ChamadaFuncao, self).__init__()
        self.name = name
        self.args = args

    def validate(self):
        if self.name not in scope.functions:
            raise Exception('Function "%s" not delcared' % self.name)
        function = scope.functions[self.name]

        if len(function.args) != len(self.args):
            error = '%d, %d' % (len(function.args), len(self.args))
            raise Exception('Number of parameters is incorrect (%s)' % error)

        for argument, parameter in zip(function.args, self.args):
            parameter.validate()
            try:
                cast(parameter.type, argument.type)
            except Exception:
                type_arg = argument.type
                type_par = parameter.type
                error = '%s, %s' % (type_arg, type_par)
                raise Exception('Types do not match (%s)' % error)


class OperacaoBinaria(Node):
    def __init__(self, left, operation, right):
        super(OperacaoBinaria, self).__init__()
        self.left = left
        self.operation = operation
        self.right = right

    def validate(self):
        self.left.validate()
        self.right.validate()

        if self.operation == OperationTypes.BOOLEAN:
            self._boolean()
            self._type = Types.BOOLEAN
        else:
            self._type = cast(self.left.type, self.right.type)

    def _boolean(self):
        left = self.left.type
        right = self.right.type
        if not (left in NumericTypes and right in NumericTypes):
            error = '(%s, %s)' % (left, right)
            raise Exception('Both sides must be numeric. Got %s' % error)


class OperacaoUnaria(Node):
    def __init__(self, operation, right):
        super(OperacaoUnaria, self).__init__()
        self.operation = operation
        self.right = right

    def validate(self):
        self.right.validate()
        if self.right.type not in NumericTypes:
            raise Exception('Unary operation must be with numbers')
        self._type = self.right.type


class LiteralValor(Node):
    def __init__(self, value, _type):
        super(LiteralValor, self).__init__()
        self.value = value
        self._type = _type

    def validate(self):
        pass
