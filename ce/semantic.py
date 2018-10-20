from abc import ABC, abstractmethod
from enum import IntEnum, auto


symbol_table = {}


class Types(IntEnum):
    CURTO = auto()
    FLUTUA = auto()
    BOOL = auto()
    VOID = auto()


class Operations(IntEnum):
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    MOD = auto()
    AND = auto()
    LE = auto()
    GE = auto()
    LT = auto()
    GT = auto()
    EQ = auto()
    NE = auto()
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
    def __init__(self, commands=[]):
        super(Bloco, self).__init__()
        self.commands = commands

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
        if self.expression.type != Types.BOOL:
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
        self.step.validate()
        self.block.validate()

        if self.condition.type != Types.BOOL:
            raise Exception('For loop condition be boolean. Got %s' % self.condition.type)

class StatementEnquanto(Node):
    def __init__(self, condition, block):
        super(StatementEnquanto, self).__init__()
        self.condition = condition
        self.block = block

    def validate(self):
        self.condition.validate()
        if self.condition.type != Types.BOOL:
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
    def __init__(self, _type, name, expression=None):
        global symbol_table
        super(DeclaracaoVariavel, self).__init__()
        self._type = _type
        self.name = name
        self.expression = expression

        symbol_table[name] = _type

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
    def __init__(self, name):
        super(Variavel, self).__init__()
        self.name = name

    def validate(self):
        global symbol_table
        if self.name not in symbol_table:
            raise Exception('Variable %s not declared' % self.name)



class ChamadaFuncao(Node):
    def __init__(self, name, args=[]):
        super(ChamadaFuncao, self).__init__()
        self.name = name
        self.args = args

    def validate(self):
        for arg in self.args:
            arg.validate()

class Argumento(Node):
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
    BOOLEAN_OPERATIONS = {
        Operations.EQ,
        Operations.NE,
        Operations.LE,
        Operations.LT,
        Operations.GE,
        Operations.GT
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

        # Check for operation type
        if self.operation in self.BOOLEAN_OPERATIONS:
            self._type = Types.BOOL
            return

        if self.operation in self.NUMERIC_TYPES:
            return self._numeric_validate()

    def _numeric_validate(self):
        types = { self.left.type, self.right.type }
        if Types.FLUTUA in types:
            self._type = Types.FLUTUA
        elif { Types.CURTO } == types:
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



class Atribuicao(Node):
    def __init__(self, name, operation):
        super(Atribuicao, self).__init__()
        self.name = name
        self.operation = operation

    def validate(self):
        self.operation.validate()



class LiteralValor(Node):
    def __init__(self, value, _type):
        super(LiteralValor, self).__init__()
        self.value = value
        self._type = _type

    def validate(self):
        pass

