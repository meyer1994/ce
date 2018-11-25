from llvmlite import ir

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
            scope[self.name] = self

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

        scope.create()
        for arg in self.args:
            arg.validate(scope)
        self.block.validate(scope)
        scope.pop()

    def generate(self, _, scope):
        args = [arg.type.value for arg in self.args]
        fnty = ir.FunctionType(self.type.value, args)

        name = '%s_module' % self.name
        module = ir.Module(name=name)

        func = ir.Function(module, fnty, name=self.name)
        name = '%s_block' % self.name
        block = func.append_basic_block(name=name)

        builder = ir.IRBuilder(block)
        args = []
        for i, arg in enumerate(func.args):
            arg.name = self.args[i].name
            args.append(arg)
            scope.current[arg.name] = arg
        func.args = tuple(args)

        self.block.generate(builder, scope)
        return builder
