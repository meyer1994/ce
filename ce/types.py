from enum import Enum
from functools import partial

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


INT_TYPES = {
    Types.SHORT,
    Types.INT,
    Types.LONG,
    # Types.BOOLEAN
}

FLOAT_TYPES = {
    Types.FLOAT,
    Types.DOUBLE
}

NUMERIC_TYPES = INT_TYPES | FLOAT_TYPES
NumericTypes = NUMERIC_TYPES


class OpTypes(Enum):
    # Numeric
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    MOD = '%'
    # Boolean
    GE = '>='
    LE = '<='
    GT = '>'
    LT = '<'
    EQ = '=='
    NE = '!='


NUMERIC_OPS = {
    OpTypes.ADD,
    OpTypes.SUB,
    OpTypes.MUL,
    OpTypes.DIV,
    OpTypes.MOD
}


BOOLEAN_OPS = {
    OpTypes.GE,
    OpTypes.LE,
    OpTypes.GT,
    OpTypes.LT,
    OpTypes.EQ,
    OpTypes.NE
}


def cast_numeric(type_a, type_b):
    '''
    Casts the types to the highest one.

    The highest priority types are in the followin order. Higher to lower:
        - Double
        - Float
        - Long
        - Int
        - Short

    Args:
        type_a: A Types enum.
        type_b: A Types enum.

    Returns:
        An enum of Types with the correct casted value.

    Raises:
        TypeError when the types are not numeric.
    '''
    if type_a == type_b:
        return type_a

    types = {type_a, type_b}

    if not (types < NumericTypes):
        types = '%s and %s' % (type_a.name, type_b.name)
        raise TypeError('Invalid types to cast. Got %s' % types)

    if Types.DOUBLE in types:
        return Types.DOUBLE
    if Types.FLOAT in types:
        return Types.FLOAT
    if Types.LONG in types:
        return Types.LONG
    if Types.INT in types:
        return Types.INT
    if Types.SHORT in types:
        return Types.SHORT


def cast_code(builder, type_a, type_b):
    '''
    Converts type_b to type_a using the builder.

    Args:
        builder: IRBUilder to use
        type_a: Types enum for type_b to be casted to
        type_b: Types enum.

    Returns:
        One parameter partial function to be called with the correct value.
    '''
    if type_a == type_b:
        return lambda x: x

    types = {type_a, type_b}
    # float to float
    if types <= FLOAT_TYPES:
        return partial(builder.fptrunc, typ=type_a.value)

    # int to int
    if types <= INT_TYPES:
        return partial(builder.trunc, typ=type_a.value)

    # int to float
    if type_a in FLOAT_TYPES:
        return partial(builder.sitofp, typ=type_a.value)

    # float to int
    if type_a in INT_TYPES:
        return partial(builder.fptosi, typ=type_a.value)


def get_operation(builder, operation, typ):
    if typ in FLOAT_TYPES:
        return float_operation(builder, operation)
    else:
        return int_operation(builder, operation)


def float_operation(builder, operation):
    table = {
        OpTypes.ADD: builder.fadd,
        OpTypes.SUB: builder.fsub,
        OpTypes.MUL: builder.fmul,
        OpTypes.DIV: builder.fdiv,
        OpTypes.MOD: builder.frem,
        OpTypes.GE: partial(builder.fcmp_ordered, OpTypes.GE.value),
        OpTypes.LE: partial(builder.fcmp_ordered, OpTypes.LE.value),
        OpTypes.GT: partial(builder.fcmp_ordered, OpTypes.GT.value),
        OpTypes.LT: partial(builder.fcmp_ordered, OpTypes.LT.value),
        OpTypes.EQ: partial(builder.fcmp_ordered, OpTypes.EQ.value),
        OpTypes.NE: partial(builder.fcmp_ordered, OpTypes.NE.value)
    }
    return table[operation]


def int_operation(builder, operation):
    table = {
        OpTypes.ADD: builder.add,
        OpTypes.SUB: builder.sub,
        OpTypes.MUL: builder.mul,
        OpTypes.DIV: builder.sdiv,
        OpTypes.MOD: builder.srem,
        OpTypes.GE: partial(builder.icmp_signed, OpTypes.GE.value),
        OpTypes.LE: partial(builder.icmp_signed, OpTypes.LE.value),
        OpTypes.GT: partial(builder.icmp_signed, OpTypes.GT.value),
        OpTypes.LT: partial(builder.icmp_signed, OpTypes.LT.value),
        OpTypes.EQ: partial(builder.icmp_signed, OpTypes.EQ.value),
        OpTypes.NE: partial(builder.icmp_signed, OpTypes.NE.value)
    }
    return table[operation]
