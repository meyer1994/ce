from ce.semantic.node import Node
from ce.types import Types, cast_code, cast_numeric, get_operation, \
    NUMERIC_TYPES, BOOLEAN_OPS


class OpBin(Node):
    def __init__(self, left, op, right):
        super(OpBin, self).__init__()
        self.left = left
        self.op = op
        self.right = right

    def validate(self, scope):
        self.left.validate(scope)
        self.right.validate(scope)

        if self.op in BOOLEAN_OPS:
            self._boolean()
            self.type = Types.BOOLEAN
        else:
            self.type = cast_numeric(self.left.type, self.right.type)

    def generate(self, builder, scope):
        left = self.left.generate(builder, scope)
        right = self.right.generate(builder, scope)

        # cast to values
        convertion = cast_code(builder, self.type, self.left.type)
        left = convertion(left)
        convertion = cast_code(builder, self.type, self.right.type)
        right = convertion(right)

        operation = get_operation(builder, self.op, self.type)
        return operation(left, right)

    def _boolean(self):
        left = self.left.type
        right = self.right.type
        if left not in NUMERIC_TYPES and right not in NUMERIC_TYPES:
            error = '%s and %s' % (left.name, right.name)
            raise Exception('Both sides must be numeric. Got %s' % error)


class OpUn(Node):
    def __init__(self, operation, right):
        super(OpUn, self).__init__()
        self.operation = operation
        self.right = right

    def validate(self, scope):
        self.right.validate(scope)
        if self.right.type not in NUMERIC_TYPES:
            raise Exception('Unary operation must be with numbers')
        self.type = self.right.type

    def generate(self, builder, scope):
        zero = self.right.type.value(0)
        right = self.right.generate(builder, scope)
        return builder.sub(zero, right)
