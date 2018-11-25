from argparse import ArgumentParser

from llvmlite import ir

from ce.scope import Scopes
from ce.parser import create_parser


def create_builder():
    '''
    Creates a simple builder for testing purposes

    The builder has a void function and an empty basic block in it.
    '''
    module = ir.Module(name='test_module')
    typ = ir.FunctionType(ir.VoidType(), ())
    function = ir.Function(module, typ, name='test_function')
    block = function.append_basic_block(name='test_block')
    return ir.IRBuilder(block)


if __name__ == '__main__':
    arg_parser = ArgumentParser(description='Parse a file')
    arg_parser.add_argument('--file', '-f', type=str, help='Parse file')
    args = arg_parser.parse_args()

    with open(args.file, 'r') as f:
        data = f.read()
        parser = create_parser()
        result = parser.parse(data)

    scope = Scopes()
    result.validate(scope)
    for r in result.commands:
        print(r)

    scope = Scopes()
    builder = create_builder()
    result.generate(builder, scope)
    print(builder.module)
