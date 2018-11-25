from ce.semantic.node import Node
from ce.types import Types, NumericTypes, cast, OperationTypes


class Block(Node):
    def __init__(self, commands=[]):
        super(Block, self).__init__()
        self.commands = commands

    def validate(self, scope):
        scope.create()
        for command in self.commands:
            command.validate(scope)
        scope.pop()


class If(Node):
    def __init__(self, expression, block, else_block=None):
        super(If, self).__init__()
        self.expression = expression
        self.block = block
        self.else_block = else_block

    def validate(self, scope):
        self.expression.validate(scope)
        if self.expression.type != Types.BOOLEAN:
            error = self.expression.type
            raise Exception('If expression must be a boolean. Got %s' % error)
        self.block.validate(scope)
        if self.else_block:
            self.else_block.validate(scope)


class For(Node):
    def __init__(self, declaration, condition, step, block):
        super(For, self).__init__()
        self.declaration = declaration
        self.condition = condition
        self.step = step
        self.block = block

    def validate(self, scope):
        self.declaration.validate(scope)
        self.condition.validate(scope)
        if self.condition.type != Types.BOOLEAN:
            error = self.condition.type
            raise Exception('For loop condition be boolean. Got %s' % error)
        self.step.validate(scope)
        self.block.validate(scope)


class While(Node):
    def __init__(self, condition, block):
        super(While, self).__init__()
        self.condition = condition
        self.block = block

    def validate(self, scope):
        self.condition.validate(scope)
        if self.condition.type != Types.BOOLEAN:
            error = self.condition.type
            raise Exception('While condition must be boolean. Got %s' % error)
        self.block.validate(scope)


class Switch(Node):
    def __init__(self, value, case_blocks=[]):
        super(Switch, self).__init__()
        self.value = value
        self.case_blocks = case_blocks

    def validate(self, scope):
        self.value.validate(scope)
        for block in self.case_blocks:
            block.validate(scope)


class Case(Node):
    def __init__(self, value, block):
        super(Case, self).__init__()
        self.value = value
        self.block = block

    def validate(self, scope):
        self.value.validate(scope)
        self.block.validate(scope)


class DeclVariable(Node):
    def __init__(self, _type, name, expression=None, dimensions=0):
        super(DeclVariable, self).__init__()
        self._type = _type
        self.name = name
        self.expression = expression
        self.dimensions = dimensions

    def validate(self, scope):
        if self.name in scope.current:
            raise Exception('Variable "%s" already declared' % self.name)
        else:
            scope.add(self)

        if self.expression is not None:
            self.expression.validate(scope)
            cast(self.expression.type, self.type)


class DeclFunction(Node):
    def __init__(self, _type, name, block, args=[]):
        super(DeclFunction, self).__init__()
        self._type = _type
        self.name = name
        self.args = args
        self.block = block

    def validate(self, scope):
        if self.name in scope.current:
            raise Exception('Function %s already declared' % self.name)
        else:
            scope.current[self.name] = self

        self.block.commands = self.args + self.block.commands
        self.block.validate(scope)


class Var(Node):
    def __init__(self, name, dimensions=0):
        super(Var, self).__init__()
        self.name = name
        self.dimensions = dimensions

    def validate(self, scope):
        var = scope.get(self.name)
        if var is None:
            raise Exception('Variable "%s" not declared' % self.name)

        if var.dimensions < self.dimensions:
            raise Exception('Trying to access bigger array dimensions')
        self._type = var.type


class Assign(Node):
    def __init__(self, var, operation):
        super(Assign, self).__init__()
        self.var = var
        self.operation = operation

    def validate(self, scope):
        self.var.validate(scope)
        self.operation.validate(scope)
        cast(self.var.type, self.operation.type)


class Call(Node):
    def __init__(self, name, args=[]):
        super(Call, self).__init__()
        self.name = name
        self.args = args

    def validate(self, scope):
        val = scope.get(self.name)
        if val is None:
            raise Exception('Function "%s" not delcared' % self.name)
        function = val

        if len(function.args) != len(self.args):
            error = '%d, %d' % (len(function.args), len(self.args))
            raise Exception('Number of parameters is incorrect (%s)' % error)

        for argument, parameter in zip(function.args, self.args):
            parameter.validate(scope)
            try:
                cast(parameter.type, argument.type)
            except Exception:
                type_arg = argument.type
                type_par = parameter.type
                error = '%s, %s' % (type_arg, type_par)
                raise Exception('Types do not match (%s)' % error)


class OpBin(Node):
    def __init__(self, left, operation, right):
        super(OpBin, self).__init__()
        self.left = left
        self.operation = operation
        self.right = right

    def validate(self, scope):
        self.left.validate(scope)
        self.right.validate(scope)

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


class OpUn(Node):
    def __init__(self, operation, right):
        super(OpUn, self).__init__()
        self.operation = operation
        self.right = right

    def validate(self, scope):
        self.right.validate(scope)
        if self.right.type not in NumericTypes:
            raise Exception('Unary operation must be with numbers')
        self._type = self.right.type


class Literal(Node):
    def __init__(self, value, _type):
        super(Literal, self).__init__()
        self.value = value
        self._type = _type

    def validate(self, scope):
        pass
