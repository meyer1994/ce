from llvmlite import ir

from ce.scope import Scopes
from ce.semantic.node import Node
from ce.types import Types, cast_code
from ce.semantic.declarations import DeclVariable, DeclFunction


class Main(Node):
    def __init__(self, commands=[]):
        super(Main, self).__init__()
        self.commands = commands
        self.module = ir.Module()

    def validate(self):
        scope = Scopes()
        with scope() as scop:
            for c in self.commands:
                c.validate(scop)

    def generate(self):
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
        # if
        with scope() as scop:
            self.block.validate(scop)
        # else
        with scope() as scop:
            self.else_block.validate(scope)

    def generate(self, builder, scope):
        expr = self.expr.generate(builder, scope)
        with builder.if_else(expr) as (then, other):
            # if
            with then:
                with scope() as scop:
                    self.block.generate(builder, scop)
            # else
            with other:
                with scope() as scop:
                    self.else_block.generate(builder, scop)
        return builder.block


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
            # declaration
            block = builder.append_basic_block('for-decl')
            builder.branch(block)
            builder.position_at_start(block)
            self.decl.generate(builder, scop)

            # condition
            block = builder.append_basic_block('for-if')
            builder.branch(block)
            builder.position_at_start(block)
            cond = self.cond.generate(builder, scop)

            # body
            with builder.if_then(cond):
                self.block.generate(builder, scop)
                self.step.generate(builder, scop)
                builder.branch(block)
        return builder.block


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
        builder.branch(block)
        builder.position_at_start(block)
        with scope() as scop:
            # condition
            cond = self.cond.generate(builder, scope)
            # body
            with builder.if_then(cond):
                self.block.generate(builder, scop)
                builder.branch(block)
            block = builder.block
        return block


class Switch(Node):
    def __init__(self, expr, cases=[]):
        super(Switch, self).__init__()
        self.expr = expr
        self.cases = cases

    def validate(self, scope):
        self.expr.validate(scope)

        if len(self.cases) == 0:
            raise SyntaxError('There must be at least one case')

        for block in self.cases:
            block.validate(scope)

    def generate(self, builder, scope):
        with scope() as scop:
            block = builder.append_basic_block('switch')
            builder.branch(block)
            builder.position_at_start(block)
            expr = self.expr.generate(builder, scope)

            # creates blocks
            blocks = [builder.append_basic_block('case') for _ in self.cases]
            exit = builder.append_basic_block('switch-exit')
            default = blocks[0]
            switch = builder.switch(expr, default)
            for block, case in zip(blocks, self.cases):
                expr = case.expr.generate(builder, scop)
                with builder.goto_block(block):
                    case.block.generate(builder, scop)
                    builder.branch(exit)
                switch.add_case(expr, block)
            builder.position_at_start(exit)
            return exit


class Case(Node):
    def __init__(self, expr, block):
        super(Case, self).__init__()
        self.expr = expr
        self.block = block

    def validate(self, scope):
        self.expr.validate(scope)
        with scope() as scop:
            self.block.validate(scop)

    def generate(self, builder, scope):
        pass


class Return(Node):
    def __init__(self, expr=None):
        super(Return, self).__init__()
        self.expr = expr

    def validate(self, scope):
        if self.expr is None:
            return
        self.expr.validate(scope)

    def generate(self, builder, scope):
        if self.expr is None:
            typ = builder.function.return_value.type
            return builder.ret(typ(None))
        expr = self.expr.generate(builder, scope)
        typ = Types(builder.function.return_value.type)
        conversion = cast_code(builder, typ, self.expr.type)
        expr = conversion(expr)
        return builder.ret(expr)
