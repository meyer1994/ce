from argparse import ArgumentParser

from ce.parser import create_parser

if __name__ == '__main__':
    arg_parser = ArgumentParser(description='Parse a file')
    arg_parser.add_argument('--file', '-f', type=str, help='Parse file')
    args = arg_parser.parse_args()

    with open(args.file, 'r') as f:
        data = f.read()
        parser = create_parser()
        parser.parse(data)

    # builder = result.generate(None, scope)

    # print(builder.module)
