"""
TODO:
- [x] One Object with all options and defaults
- [x] Create one parser
- [ ] First parse the argument parser (for config file)
- [ ] Then parse the config file
- [ ] Then parse rest of arguments
- [ ] Overwrite current value in the dict


Perpahs make it class based??

"""
import argparse
import os
from typing import Dict
from typing import List
from typing import Tuple

from notesystem.modes.check_mode.check_mode import ALL_ERRORS
from notesystem.modes.check_mode.errors.base_errors import BaseError

CONFIG_FILE_NAME = '.notesystem'
CONFIG_FILE_LOCATIONS = [
    '~/.config/.notesystem',
    os.path.abspath(os.path.join(os.getcwd())),
]


def _create_option_disabled_error(error: BaseError):
    """Helper function to create the options for the disabled errors"""
    return {
        'group_name': 'Disabled Errors',
        'group_desc': 'Using these flags you can disable checking for certain errors',  # noqa: E501
        'value': None,
        'flags': [f'--disable-{error.get_error_name()}'],
        'config_name': f'disable_{error.get_error_name()}',
        'help': f'Disable: {error.get_help_text()}',
        'action': 'store_true',
        'type': bool,
        'default': False,
        'dest': f'd-{error.get_error_name()}',
    }


OPTIONS = {
    'general': {
        'verbose': {
            'value': None,
            'flags': ['-v', '--verbose'],
            'config_name': 'verbose',
            'help': 'enable verbose mode (print debug output)',
            'action': 'store_true',
            'type': bool,
            'default': False,
            'required': False,
        },
        'visual': {
            'value': None,
            'flags': ['--no-visual'],
            'config_name': 'no_visual',
            'help': 'enable visual mode (is enabled by default)',
            'action': 'store_true',
            'type': bool,
            'default': True,
            'required': False,
        },
        'config_file': {
            'value': None,
            'flags': ['--config-file'],
            'config_name': None,  # Only command line flag
            'help': 'the path to your config file',
            'type': str,
            'default': None,
            'required': False,
            'metavar': 'path',
        },
    },
    'convert': {
        'in_path': {
            'value': None,
            'flags': ['in_path'],
            'config_name': None,  # Only command line flag
            'help': 'the file/folder to be converted',
            'type': str,
            'metavar': 'in',
            'default': None,
        },
        'out_path': {
            'value': None,
            'flags': ['out_path'],
            'config_name': None,  # Only command line flag
            'help': 'the path to write the converted file(s) to',
            'type': str,
            'metavar': 'out',
            'default': None,
        },
        'watch': {
            'value': None,
            'flags': ['--watch', '-w'],
            'config_name': 'watch',
            'help': 'enables watch mode (convert files that have changed)',
            'type': bool,
            'action': 'store_true',
            'default': False,
        },
        'pandoc_args': {
            'value': None,
            'flags': ['--pandoc-args'],
            'config_name': 'pandoc_args',
            'help': "specify the arguments that need to based on to pandoc. \
                     E.g.: --pandoc-args='--standalone --preserve-tabs'",
            'type': str,
            'metavar': 'ARGS',
            'default': '',
        },
        'pandoc_template': {
            'value': None,
            'flags': ['--pandoc-template'],
            'config_name': 'pandoc_template',
            'help': 'specify a template for pandoc to use in convertion. \
                     Default: GitHub.html5 (for md to html)',
            'type': str,
            'metavar': 'T',
            # Perhaps not needed? Because it is defaulted in the code?
            'default': 'Github.html5',
        },
        'to_pdf': {
            'value': None,
            'flags': ['--to-pdf'],
            'config_name': 'to_pdf',
            'help': 'convert the markdown files to pdf instead of html. \
                     Note: No template is used by default.',
            'type': bool,
            'action': 'store_true',
            'default': False,
        },
        'ignore_warnings': {
            'value': None,
            'flags': ['--ingore-warnings'],
            'config_name': 'ignore_warnings',
            'help': 'ignore warnings from pandoc',
            'type': bool,
            'action': 'store_true',
            'default': False,
        },
    },
    'check': {
        'in_path': {
            'value': None,
            'flags': ['in_path'],
            'config_name': None,  # Only command line flag
            'help': 'the file/folder to be converted',
            'type': str,
            'metavar': 'in',
            'default': None,
        },
        'fix': {
            'value': None,
            'flags': ['--fix', '-f'],
            'config_name': 'fix',  # Only command line flag
            'help': 'enables auto fixing for problems in the documents',
            'action': 'store_true',
            'type': bool,
            'default': False,
        },
        'disabled_errors': [
            _create_option_disabled_error(error)  # type: ignore
            for error in ALL_ERRORS
        ],
    },
}


def _gen_argparse_args(opts: dict) -> Tuple[List[str], Dict]:
    """Generate the arguments for ArgumentParser.add_argument()

    Returns:
        Tuple[List[str], Dict] - The first arguments (*args) and the **kwargs
                                 for add_argument()
    """
    flag_or_pos = []
    fn_args = {}
    # Perhaps a better way to do this always add the option
    # except when it is not an argparse option
    # e.g.: 'config_name' or 'type', or 'required' (in some cases)
    for o in opts:
        if o == 'flags':
            flag_or_pos = opts[o]
        elif o == 'help':
            fn_args['help'] = opts[o]
        elif o == 'default':
            fn_args['default'] = opts[o]
        elif o == 'action':
            fn_args['action'] = opts[o]
        elif o == 'value':
            continue
        elif o == 'config_name':
            continue
        elif o == 'type':
            continue
        elif o == 'metavar':
            fn_args['metavar'] = opts[o]
        elif o == 'dest':
            fn_args['dest'] = opts[o]
        elif o == 'required':
            # This assumes that flags is always defined before required...
            if len(flag_or_pos) >= 1 and not flag_or_pos[0].startswith('-'):
                # Only add required to flags
                # Argparse will not accept required on positional arguments
                fn_args['required'] = opts[o]
        else:
            print('Found an unknown option')
            print(o, opts[o])

    return (flag_or_pos, fn_args)


def create_parsers() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='notesystem',
        description='A system for handing your notes for you',
    )
    # Create the convert and check parsers
    mode_parser = parser.add_subparsers(
        title='modes',
        description='choose a mode to use',
        help='use {convert, check} --help to view more options',
    )
    convert_parser = mode_parser.add_parser(
        'convert',
        help='convert files from markdown to html (by default) or to pdf \
             (using --to-pdf)',
    )
    convert_parser.set_defaults(mode='convert')
    check_parser = mode_parser.add_parser(
        'check',
        help='check markdown file(s) for styling errors',
    )
    check_parser.set_defaults(mode='check')

    # Parse the OPTIONS dict and create the argparser
    for section in OPTIONS:
        if section == 'general':
            # Create the main parser
            for option in OPTIONS[section]:
                opts = _gen_argparse_args(
                    OPTIONS[section][option],  # type: ignore
                )
                parser.add_argument(*opts[0], **opts[1])  # type: ignore
        elif section == 'convert':
            for option in OPTIONS[section]:
                opts = _gen_argparse_args(
                    OPTIONS[section][option],  # type: ignore
                )
                convert_parser.add_argument(*opts[0], **opts[1])
        elif section == 'check':
            for option in OPTIONS[section]:
                # Handle disabled errors (is a list)
                if isinstance(OPTIONS[section][option], list):
                    op = OPTIONS[section][option]
                    if len(op) < 1:  # type: ignore
                        continue
                    assert 'group_name' in op[0]  # type: ignore
                    assert 'group_desc' in op[0]  # type: ignore
                    new_group = check_parser.add_argument_group(
                        op[0]['group_name'],  # type: ignore
                        op[0]['group_desc'],  # type: ignore
                    )
                    for i in OPTIONS[section][option]:  # type: ignore
                        opts = _gen_argparse_args(i)
                        new_group.add_argument(*opts[0], **opts[1])
                else:
                    opts = _gen_argparse_args(
                        OPTIONS[section][option],  # type: ignore
                    )
                    check_parser.add_argument(*opts[0], **opts[1])
            pass
        else:
            # ERROR
            continue
    return parser
