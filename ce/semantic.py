from abc import ABC, abstractmethod
from enum import IntEnum, auto
from copy import deepcopy


functions = {}


class Scopes(object):
    def __init__(self):
        super(Scopes, self).__init__()
        self.scopes = [ {} ]

    def create(self):
        self.scopes.append({})

    def pop(self):
        return self.scopes.pop()

    @property
    def current(self):
        return self.scopes[-1]

    def get(self, name):
        for s in reversed(self.scopes):
            if name in s:
                return s[name]
        return None


scope = Scopes()


class Types(IntEnum):
    NUMERICO = auto()
    OPINIAO = auto()
    LETRA = auto()
    LETRAS = auto()
    NADA = auto()
    FUNCAO = auto()

class Operations(IntEnum):
    NUMERICO = auto()
    OPINIAO = auto()



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
        scope.create()
        self.validate()
        scope.pop()

    def validate(self):
        for command in self.commands:
            command.validate()

class StatementSe(Node):
    def __init__(self, expression, block, else_block=None):
        super(StatementSe, self).__init__()
        self.expression = expression
        self.block = block
        self.else_block = else_block

    def validate(self):
        self.expression.validate()
        if self.expression.type != Types.OPINIAO:
            raise Exception('If expression should return a boolean')

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
        if self.condition.type != Types.OPINIAO:
            raise Exception('For loop condition be boolean. Got %s' % self.condition.type)

        self.step.validate()
        self.block.validate()

class StatementEnquanto(Node):
    def __init__(self, condition, block):
        super(StatementEnquanto, self).__init__()
        self.condition = condition
        self.block = block

    def validate(self):
        self.condition.validate()
        if self.condition.type != Types.OPINIAO:
            raise Exception('While condition must be boolean. Got %s' % self.condition.type)

        self.block.validate()

class StatementCaso(Node):
    def __init__(self, value, case_blocks):
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

        if name in scope.current:
            raise Exception('Redeclaration of variable "%s"' % name)
        scope.current[name] = (_type, dimensions)

    def validate(self):
        if self.expression:
            self.expression.validate()
            if self.expression.type != self.type:
                error = '(%s and %s)' % (self.type, self.expression.type)
                raise Exception('Assigning different types %s' % error)

class DeclaracaoFuncao(Node):
    def __init__(self, _type, name, block, args=[]):
        super(DeclaracaoFuncao, self).__init__()
        self._type = _type
        self.name = name
        self.args = args
        self.block = block

        if name in functions:
            raise Exception('Redeclaration of function %s' % name)
        functions[name] = (_type, args)

        for arg in args:
            scope.current[arg.name] = (arg.type, arg.dimensions)


    def validate(self):
        self.block.validate()



class Variavel(Node):
    def __init__(self, name, dimensions=0):
        super(Variavel, self).__init__()
        self.name = name
        self.dimensions = dimensions

    def validate(self):
        var = scope.get(self.name)
        if var is None:
            raise Exception('Variable "%s" not declared' % self.name)

        _type, dimensions = var
        if dimensions < self.dimensions:
            raise Exception('Trying to access bigger dimensions')
        self._type = _type


class Atribuicao(Node):
    def __init__(self, var, operation):
        super(Atribuicao, self).__init__()
        self.var = var
        self.operation = operation

    def validate(self):
        self.operation.validate()
        self.var.validate()

        if self.var.type != self.operation.type:
            types = '%s to %s' % (self.operation.type, self.var.type)
            raise Exception('Trying to attribute %s' % types)



class ChamadaFuncao(Node):
    def __init__(self, name, args=[]):
        super(ChamadaFuncao, self).__init__()
        self.name = name
        self.args = args

    def validate(self):
        if self.name not in functions:
            raise Exception('Function "%s" not delcared' % self.name)

        _type, args = functions[self.name]
        self._type = _type

        for arg, par in zip(args, self.args):
            par.validate()
            if arg.type != par.type:
                raise Exception('Invalid types passed in function call')

class Argumento(Node):
    def __init__(self, _type, name, dimensions=0):
        super(Argumento, self).__init__()
        self._type = _type
        self.name = name
        self.dimensions = 0

        scope.current[name] = (_type, dimensions)

    def validate(self):
        pass




class OperacaoBinaria(Node):
    def __init__(self, left, operation, right):
        super(OperacaoBinaria, self).__init__()
        self.left = left
        self.operation = operation
        self.right = right

    def validate(self):
        # Check for valid operation
        if not isinstance(self.operation, Operations):
            raise Exception('Invalid operation. Got %s' % self.operation)

        # Validate children
        self.left.validate()
        self.right.validate()

        if self.operation == Operations.OPINIAO:
            return self._boolean_validate()

        if self.left.type == Types.NUMERICO and self.right.type == Types.NUMERICO:
            self._type = Types.NUMERICO

    def _boolean_validate(self):
        if self.right.type != self.left.type:
            types = '%s and %s' % (self.left.type, self.right.type)
            raise Exception('Values types do not match (%s)' % types)
        self._type = Types.OPINIAO

class OperacaoUnaria(Node):
    def __init__(self, operation, right):
        super(OperacaoUnaria, self).__init__()
        self.operation = operation
        self.right = right

    def validate(self):
        self.right.validate()

        # Check for valid type
        if self.right.type != Operations.NUMERICO:
            raise Exception('Operations can only be performed with numbers')

        # Set own type
        self._type = self.right.type



class LiteralValor(Node):
    def __init__(self, value, _type):
        super(LiteralValor, self).__init__()
        self.value = value
        self._type = _type

    def validate(self):
        pass
