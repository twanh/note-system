import argparse
import logging
import sys
from typing import Optional, Sequence

from termcolor import colored

from notesystem.modes.base_mode import ModeOptions
from notesystem.modes.convert_mode import ConvertMode, ConvertModeArguments
from notesystem.modes.check_mode.check_mode import CheckMode


# TODO: Move the creating of sub parsers to the mode


def create_argparser() -> argparse.ArgumentParser:
    """Parse the command line arguments

    Returns:
        ArgumentParser
    """

    # General parser
    parser = argparse.ArgumentParser(
        prog='notesystem',
        description='A system for handling your notes for you',
    )
    # To enable verbose mode
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='enable verbose mode (print debug output)',
        default=False,
    )

    # Create convert, check subcommands
    mode_parser = parser.add_subparsers(
        title='modes',
        description='choose a mode to use',
        help='use {convert, check} --help to view more options',
    )

    # Convert parser
    # Used for the convert mode,
    convert_parser = mode_parser.add_parser(
        'convert',
        help='convert files from markdown to html',
    )
    # Set a default, so later on it is clear whith mode is used
    convert_parser.set_defaults(mode='convert')
    # Add argumens
    convert_parser.add_argument(
        'in_path',
        metavar='in',
        help='the file/folder to be converted',
        type=str,
    )
    convert_parser.add_argument(
        'out_path',
        metavar='out',
        help='the path to write the converted file(s) to',
        type=str,
    )

    convert_parser.add_argument(
        '--watch',
        '-w',
        help='enables watch mode (convert files that have changed as soon as they have changed)',
        action='store_true',
        default=False,
    )

    # Check parser
    # Used for the checking mode
    check_parser = mode_parser.add_parser(
        'check',
        help='check markdown file(s) for styling errors',
    )
    # Set a default, so later on it is clear which mode is used
    check_parser.set_defaults(mode='check')
    check_parser.add_argument(
        'in_path',
        metavar='in',
        help='the file/folder to be checked',
        type=str,
    )
    # To enable autofixing
    check_parser.add_argument(
        '--fix',
        '-f',
        action='store_true',
        help='enables auto fixing for problems in the documents',
        default=False,
    )

    return parser


def main(argv: Optional[Sequence[str]] = None):

    if argv is None:
        argv = sys.argv[1:]

    # Create logger
    logging.basicConfig(
        format='[%(levelname)s:%(name)s] @ %(asctime)s: %(message)s',
        datefmt='%H:%M:%S',
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.ERROR)

    # Parse arguments
    parser = create_argparser()
    args = vars(parser.parse_args(argv))
    if args['verbose']:
        logging.getLogger().setLevel(logging.INFO)

    # Define modes
    convert_mode = ConvertMode()
    check_mode = CheckMode()

    if 'mode' not in args:
        parser.print_usage()
        sys.exit(1)

    if args['mode'] == 'check':
        mode_options: ModeOptions = {
            'visual': True,
            'args': {
                'in_path': args['in_path'],
                'fix': args['fix'],
            },

        }
        check_mode.start(mode_options)
    elif args['mode'] == 'convert':
        convert_mode_options: ModeOptions = {
            'visual': True,
            'args': {
                'in_path': args['in_path'],
                'out_path': args['out_path'],
                'watch': args['watch'],
            },
        }
        convert_mode.start(convert_mode_options)


if __name__ == '__main__':
    main()
