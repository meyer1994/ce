from ce.semantic.node import Node
from ce.types import cast


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


class Literal(Node):
    def __init__(self, value, _type):
        super(Literal, self).__init__()
        self.value = value
        self._type = _type

    def validate(self, scope):
        pass
