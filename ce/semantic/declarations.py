from functools import reduce

from llvmlite import ir

from ce.semantic.node import Node
from ce.types import cast_numeric, cast_code


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

        # Add itself to scope
        scope[self.name] = self

        if self.expr is None:
            return
        self.expr.validate(scope)
        cast_numeric(self.expr.type, self.type)

    def generate(self, builder, scope):
        size = reduce(lambda x, y: x * y.value, self.dims, 1)
        ptr = builder.alloca(self.type.value, size, self.name)

        # Adds itself to scope
        scope[self.name] = ptr

        if self.expr is None:
            return ptr

        # Proper conversions and casting
        expr = self.expr.generate(builder, scope)
        convertion = cast_code(builder, self.type, self.expr.type)
        expr = convertion(expr)
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

        # Adds itself
        scope[self.name] = self

        # Validate function block and args
        with scope() as scop:
            for arg in self.args:
                arg.validate(scop)
            self.block.validate(scop)

    def generate(self, module, scope):
        self.function = self._create_function(module)

        # Adds itself to scope
        scope[self.name] = self

        # Append block
        block = self.function.append_basic_block(self.name)
        builder = ir.IRBuilder(block)

        # Generate function body
        with scope() as scop:
            self._allocate_args(builder, scop)
            gen = self.block.generate(builder, scop)
            builder.branch(gen)
        return builder

    def _allocate_args(self, builder, scope):
        ''' Allocates the passed args of the function to the function body. '''
        for arg, par in zip(self.args, self.function.args):
            ptr = arg.generate(builder, scope)
            builder.store(par, ptr)

    def _create_function(self, module):
        ''' Creates the function '''
        # Get types
        args = (arg.type.value for arg in self.args)
        function_types = ir.FunctionType(self.type.value, args)
        # Create function
        func = ir.Function(module, function_types, name=self.name)
        return func
