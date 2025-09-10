import argparse

class CombinedFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

def register_parser(subparsers):
    command = 'cli'
    description="CLI"
    parser = subparsers.add_parser(
            command,
            help=description,
            description=description,
            formatter_class=CombinedFormatter,
    )

    parser.add_argument("-v", action="store_true", help="Print the version of the package.")

    parser.set_defaults(command=command)

def main(args):
    pass
