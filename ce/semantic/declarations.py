from ce.semantic.node import Node
from ce.types import cast


class DeclVariable(Node):
    def __init__(self, typ, name, expression=None, dimensions=0):
        super(DeclVariable, self).__init__()
        self.type = typ
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

    def generate(self, builder, scope):
        ptr = builder.alloca(self.type.value, name=self.name)
        scope.current[self.name] = ptr
        return ptr


class DeclFunction(Node):
    def __init__(self, typ, name, block, args=[]):
        super(DeclFunction, self).__init__()
        self.type = typ
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
