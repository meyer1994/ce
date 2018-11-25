from ce.semantic.node import Node
from ce.types import OperationTypes, NumericTypes, Types, cast


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
            self.type = Types.BOOLEAN
        else:
            self.type = cast(self.left.type, self.right.type)


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
        self.type = self.right.type
