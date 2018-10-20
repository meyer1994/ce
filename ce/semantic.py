from abc import ABC, abstractmethod
from enum import IntEnum, auto


symbol_table = {}


class Types(IntEnum):
    CURTO = auto()
    FLUTUA = auto()


class Operations(IntEnum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    AND = auto()
    OR = auto()
    XOR = auto()
    UMINUS = auto()


class Type(object):
    def __init__(self, typ):
        super(Type, self).__init__()
        self.type = typ
        if not isinstance(self.type, Types):
            raise Exception('Invalid type. Got %s' % self.type)



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
    def __init__(self, commands):
        super(Block, self).__init__()
        self.commands = commands

    def validate(self):
        for command in self.commands:
            command.validate()



class DeclaracaoVariavel(Node):
    def __init__(self, _type, name, expression=None):
        super(DeclaracaoVariavel, self).__init__()
        self._type = _type
        self.name = name
        self.expression = expression

    def validate(self):
        if self.expression:
            self.expression.validate()

class DeclaracaoFuncao(Node):
    def __init__(self, _type, name, args=[], block=[]):
        super(DeclaracaoFuncao, self).__init__()
        self._type = _type
        self.name = name
        self.args = args
        self.block = block

    def validate(self):
        self.block.validate()



class Variavel(Node):
    def __init__(self, _type, name):
        super(Variavel, self).__init__()
        self._type = _type
        self.name = name

    def validate(self):
        pass



class ChamadaFuncao(Node):
    def __init__(self, name, args=[]):
        super(ChamadaFuncao, self).__init__()
        self.name = name
        self.args = args

    def validate(self):
        for arg in self.args:
            arg.validate()

class Argumento(object):
    def __init__(self, _type, name):
        super(Argumento, self).__init__()
        self._type = _type
        self.name = name

    def validate(self):
        pass



class Operacao(Node):
    NUMERIC_TYPES = {
        Types.FLUTUA,
        Types.CURTO
    }

class OperacaoBinaria(Operacao):
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

        # Check if children are of valid types
        if { self.left.type, self.right.type } > OperacaoBinaria.NUMERIC_TYPES:
            raise Exception('Operations can only be performed with numbers')

        # Assign your own type
        if Types.FLUTUA in { self.left.type, self.right.type }:
            self._type = Types.FLUTUA
        else:
            self._type = Types.CURTO

class OperacaoUnaria(Operacao):
    def __init__(self, operation, right):
        super(OperacaoUnaria, self).__init__()
        self.operation
        self.right

    def validate(self):
        # Check if operations is valid
        if not isinstance(self.operation, Operations):
            raise Exception('Invalid operation. Got %s' % self.operation)

        # Valid child
        self.right.validate()

        # Check for valid type
        if self.right.type not in OperacaoUnaria.NUMERIC_TYPES:
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

