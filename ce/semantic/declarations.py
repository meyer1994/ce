from functools import reduce

from llvmlite import ir

from ce.semantic.node import Node
from ce.types import cast


class DeclVariable(Node):
    def __init__(self, typ, name, expr=None, dims=[]):
        super(DeclVariable, self).__init__()
        self.type = typ
        self.name = name
        self.expr = expr
        self.dims = dims

    def validate(self, scope):
        if self.name in scope.current:
            raise Exception('Variable "%s" already declared' % self.name)
        else:
            scope[self.name] = self

        if self.expr is not None:
            self.expr.validate(scope)
            cast(self.expr.type, self.type)

    def generate(self, builder, scope):
        size = reduce(lambda x, y: x * y.value, self.dims, 1)
        ptr = builder.alloca(self.type.value, size, self.name)
        scope.current[self.name] = ptr

        if self.expr is None:
            return ptr
        expr = self.expr.generate(builder, scope)
        builder.store(expr, ptr)
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

        with scope() as scop:
            for arg in self.args:
                arg.validate(scop)
            self.block.validate(scop)

    def generate(self, module, scope):
        args = [arg.type.value for arg in self.args]
        fnty = ir.FunctionType(self.type.value, args)

        func = ir.Function(module, fnty, name=self.name)
        self.function = func
        scope[self.name] = self

        block = func.append_basic_block()

        args = []
        for i, arg in enumerate(func.args):
            arg.name = self.args[i].name
            args.append(arg)
        func.args = tuple(args)

        with scope() as scop:
            builder = ir.IRBuilder(block)
            for arg in self.args:
                ptr = builder.alloca(arg.type.value)
                scop[arg.name] = ptr
            self.block.generate(builder, scop)
        return builder
