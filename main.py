from argparse import ArgumentParser

from ce.parser import create_parser


def parse(file, debug=True):
    parser = create_parser(debug)
    with open(args.file, 'r') as f:
        data = f.read()
        parser = create_parser()
        result = parser.parse(data)
    return result


if __name__ == '__main__':
    arg_parser = ArgumentParser(description='Parse a file')
    arg_parser.add_argument('--file', '-f', type=str, help='Parse file')
    arg_parser.add_argument(
        '--generate',
        '-g',
        type=bool,
        default=True,
        help='Generate code'
    )
    args = arg_parser.parse_args()

    if args.file is not None:
        tree = parse(args.file)
        tree.validate()
        if args.generate:
            result = tree.generate()
            print(result)
