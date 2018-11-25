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
