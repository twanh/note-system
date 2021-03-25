import argparse
import logging
import sys
from typing import Optional, Sequence

from termcolor import colored

from notesystem.modes.base_mode import ModeOptions
from notesystem.modes.convert_mode import ConvertMode, ConvertModeArguments, PandocOptions
from notesystem.modes.check_mode.check_mode import CheckMode, ALL_ERRORS


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

    convert_parser.add_argument(
        '--pandoc-args',
        help="specify the arguments that need to based on to pandoc. E.g.: --pandoc-args='--standalone --preserve-tabs'",
        metavar='ARGS',
    )

    convert_parser.add_argument(
        '--pandoc-template',
        help='Specify a template for pandoc to use in convertion. Default: GitHub.html5',
        metavar='T',
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

    # Disable certain errors
    disable_errors_group = check_parser.add_argument_group(
        'Disable error types', 'Using these flags you can disable checking for certain errors',
    )

    for error in ALL_ERRORS:
        disable_error_flag = f'--disable-{error.get_error_name()}'
        help_text = f'Disable: {error.get_help_text()}'
        disable_errors_group.add_argument(
            disable_error_flag,
            action='store_true',
            help=help_text,
            dest=f'd-{error.get_error_name()}',
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

        # Extra parsing of the args to pass disabled errors more easily
        disabled_errors = []
        for arg_name in args.keys():
            if arg_name.startswith('d'):
                if args[arg_name] == True:
                    disabled_errors.append(arg_name[2:])

        mode_options: ModeOptions = {
            'visual': True,
            'args': {
                'in_path': args['in_path'],
                'fix': args['fix'],
                'disabled_errors': disabled_errors,
            },

        }
        check_mode.start(mode_options)
    elif args['mode'] == 'convert':
        pandoc_options: PandocOptions = {
            'arguments': args['pandoc_args'],
            'template': args['pandoc_template'],
        }
        convert_mode_options: ModeOptions = {
            'visual': True,
            'args': {
                'in_path': args['in_path'],
                'out_path': args['out_path'],
                'watch': args['watch'],
                'pandoc_options': pandoc_options,
            },
        }
        convert_mode.start(convert_mode_options)


if __name__ == '__main__':
    main()
