from ce.semantic.node import Node
from ce.types import cast


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
        cast(self.var.type, self.expr.type)

    def generate(self, builder, scope):
        ptr = scope.get(self.var.name)
        expr = self.expr.generate(builder, scope)
        return builder.store(expr, ptr)


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


class Literal(Node):
    def __init__(self, value, typ):
        super(Literal, self).__init__()
        self.value = value
        self.type = typ

    def validate(self, scope):
        pass

    def generate(self, _, scope):
        return self.type.value(self.value)
