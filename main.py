from argparse import ArgumentParser
from ctypes import CFUNCTYPE, c_int32, c_int64

import llvmlite.binding as llvm

from ce.parser import create_parser


def parse(filename):
    ''' Parses the passed filename '''
    parser = create_parser()
    with open(filename, 'r') as f:
        data = f.read()
        parser = create_parser()
        result = parser.parse(data)
    return result


def create_argparse():
    ''' Creates the argument parser '''
    arg_parser = ArgumentParser(description='Parse a file')
    arg_parser.add_argument(
        '--file',
        '-f',
        type=str,
        help='Parse file',
        required=True
    )
    return arg_parser


arg_parser = create_argparse()
args = arg_parser.parse_args()
result = parse(args.file)

result.validate()
module = result.generate()

# remove first 3 lines of module
module = str(module)
module = module.split('\n', 3)[3]

print(module)
