from enum import Enum, auto

from llvmlite import ir


class Types(Enum):
    VOID = ir.VoidType()
    SHORT = ir.IntType(16)
    INT = ir.IntType(32)
    LONG = ir.IntType(64)
    FLOAT = ir.FloatType()
    DOUBLE = ir.DoubleType()
    BOOLEAN = ir.IntType(1)
    CHAR = ir.IntType(8)
    STRING = ir.PointerType(ir.IntType(8))


NumericTypes = {
    Types.SHORT,
    Types.INT,
    Types.LONG,
    Types.FLOAT,
    Types.DOUBLE
}


class OperationTypes(Enum):
    BOOLEAN = auto()
    NUMERIC = auto()


def cast(type_a, type_b):
    ''' Check both passed types and cast to the proper one, if possible. '''
    types = {type_a, type_b}

    # cast to numbers
    if types <= NumericTypes:
        if Types.DOUBLE in types:
            return Types.DOUBLE
        if Types.FLOAT in types:
            return Types.FLOAT
        if Types.LONG in types:
            return Types.LONG
        if Types.INT in types:
            return Types.FLOAT
        if Types.SHORT in types:
            return Types.SHORT

    # If they are not the same, raise an error
    if len(types) != 1:
        raise Exception('Incompatible types (%s, %s)' % (type_a, type_b))

    return types.pop()
