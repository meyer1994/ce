from llvmlite import ir

from ce.types import Types
from ce.scope import Scopes
from ce.semantic.node import Node
from ce.semantic.declarations import DeclVariable, DeclFunction


class Main(Node):
    def __init__(self, commands=[]):
        super(Main, self).__init__()
        self.commands = commands
        self.module = ir.Module()

    def validate(self, scope=None):
        scope = Scopes()
        with scope() as scop:
            for comm in self.commands:
                comm.validate(scop)

    def generate(self, builder=None, scope=None):
        scope = Scopes()
        for comm in self.commands:
            if isinstance(comm, DeclVariable):
                ptr = self._var(comm)
                scope[comm.name] = ptr
            if isinstance(comm, DeclFunction):
                comm.generate(self.module, scope)
        return self.module

    def _var(self, comm):
        var = ir.GlobalVariable(self.module, comm.type.value, comm.name)
        if comm.expr is None:
            return
        var.initializer = comm.expr.generate(None, None)
        return var


class Block(Node):
    def __init__(self, commands=[]):
        super(Block, self).__init__()
        self.commands = commands

    def validate(self, scope):
        for command in self.commands:
            command.validate(scope)

    def generate(self, builder, scope):
        return [c.generate(builder, scope) for c in self.commands]


class If(Node):
    def __init__(self, expr, block, else_block=Block()):
        super(If, self).__init__()
        self.expr = expr
        self.block = block
        self.else_block = else_block

    def validate(self, scope):
        self.expr.validate(scope)
        if self.expr.type != Types.BOOLEAN:
            error = self.expr.type
            raise Exception('Expression must be a boolean. Got %s' % error)

        with scope() as scop:
            self.block.validate(scop)

        with scope() as scop:
            self.else_block.validate(scope)

    def generate(self, builder, scope):
        expr = self.expr.generate(builder, scope)
        with builder.if_else(expr) as (then, other):
            with then:
                with scope() as scop:
                    if_block = self.block.generate(builder, scop)
            with other:
                with scope() as scop:
                    else_block = self.else_block.generate(builder, scop)
        return (if_block, else_block)


class For(Node):
    def __init__(self, decl, cond, step, block):
        super(For, self).__init__()
        self.decl = decl
        self.cond = cond
        self.step = step
        self.block = block

    def validate(self, scope):
        with scope() as scop:
            self.decl.validate(scop)
            cond = If(self.cond, self.block)
            cond.validate(scop)
            self.step.validate(scop)

    def generate(self, builder, scope):
        with scope() as scop:
            self.decl.generate(builder, scop)
            block = builder.append_basic_block('for')
            builder.position_at_start(block)
            cond = self.cond.generate(builder, scop)
            with builder.if_then(cond):
                self.block.generate(builder, scop)
                self.step.generate(builder, scop)
                builder.branch(block)
        block = builder.append_basic_block()
        builder.position_at_start(block)
        return block


class While(Node):
    def __init__(self, cond, block):
        super(While, self).__init__()
        self.cond = cond
        self.block = block

    def validate(self, scope):
        self.cond.validate(scope)
        if self.cond.type != Types.BOOLEAN:
            error = self.cond.type
            raise Exception('While condition must be boolean. Got %s' % error)
        with scope() as scop:
            self.block.validate(scop)

    def generate(self, builder, scope):
        block = builder.append_basic_block('while')
        builder.position_at_start(block)
        cond = self.cond.generate(builder, scope)
        with scope() as scop:
            with builder.if_then(cond):
                self.block.generate(builder, scop)
                builder.branch(block)
        block = builder.append_basic_block()
        builder.position_at_start(block)
        return block


class Switch(Node):
    def __init__(self, value, cases=[]):
        super(Switch, self).__init__()
        self.value = value
        self.cases = cases

    def validate(self, scope):
        self.value.validate(scope)
        for block in self.cases:
            block.validate(scope)

    def generate(self, builder, scope):
        with scope() as scop:
            value = self.value.generate(builder, scop)
            results = [c.generate(builder, scop, value) for c in self.cases]
        return results


class Case(Node):
    def __init__(self, value, block):
        super(Case, self).__init__()
        self.value = value
        self.block = block

    def validate(self, scope):
        self.value.validate(scope)
        with scope() as scop:
            self.block.validate(scop)

    def generate(self, builder, scope, val):
        value = self.value.generate(builder, scope)
        cond = builder.icmp_signed('==', val, value)
        with builder.if_then(cond):
            with scope() as scop:
                return self.block.generate(builder, scop)


class Return(Node):
    def __init__(self, expr=None):
        super(Return, self).__init__()
        self.expr = expr

    def validate(self, scope):
        self.expr.validate(scope)

    def generate(self, builder, scope):
        expr = self.expr.generate(builder, scope)
        return builder.ret(expr)
