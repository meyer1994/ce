from ce.semantic.node import Node
from ce.types import cast_numeric, cast_code


class Var(Node):
    def __init__(self, name, dims=[]):
        super(Var, self).__init__()
        self.name = name
        self.dims = dims

    def validate(self, scope):
        var = scope.get(self.name)
        if var is None:
            raise Exception('Variable "%s" not declared' % self.name)
        if len(var.dims) < len(self.dims):
            raise Exception('Trying to access bigger array dimensions')
        self.type = var.type

    def generate(self, builder, scope):
        ptr = scope.get(self.name)
        return builder.load(ptr)


class Assign(Node):
    def __init__(self, var, expr):
        super(Assign, self).__init__()
        self.var = var
        self.expr = expr

    def validate(self, scope):
        self.var.validate(scope)
        self.expr.validate(scope)
        cast_numeric(self.var.type, self.expr.type)

    def generate(self, builder, scope):
        ptr = scope.get(self.var.name)
        expr = self.expr.generate(builder, scope)
        conversion = cast_code(builder, self.var.type, self.expr.type)
        expr = conversion(expr)
        return builder.store(expr, ptr)


class Call(Node):
    def __init__(self, name, args=[]):
        super(Call, self).__init__()
        self.name = name
        self.args = args

    def validate(self, scope):
        function = scope.get(self.name)
        if function is None:
            raise LookupError('Function "%s" not delcared' % self.name)
        self.type = function.type
        self.function = function
        self._check_args_list(scope)

    def generate(self, builder, scope):
        func = scope.get(self.name)
        args = [a.generate(builder, scope) for a in self.args]
        return builder.call(func.function, args)

    def _check_args_list(self, scope):
        ''' Checks if the argument list passed matches '''
        stored = self.function.args
        passed = self.args
        # Checks size
        if len(stored) != len(passed):
            error = '%d and %d' % (len(stored), len(passed))
            raise TypeError('Number of parameters is incorrect (%s)' % error)

        # Check types
        for stor, passd in zip(stored, passed):
            passd.validate(scope)
            try:
                cast_numeric(passd.type, stor.type)
            except TypeError:
                error = '%s, %s' % (stor.type, passd.type)
                raise TypeError('Types do not match (%s)' % error)


class Literal(Node):
    def __init__(self, value, typ):
        super(Literal, self).__init__()
        self.value = value
        self.type = typ

    def validate(self, scope):
        pass

    def generate(self, _, scope):
        return self.type.value(self.value)
