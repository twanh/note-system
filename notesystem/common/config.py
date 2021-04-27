# type: ignore
"""
Provides the configuration funcitonallity for notesystem

Note: types are ignored because working with a large (complex) dict (OPTIONS).

"""
import argparse
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Tuple

import toml

from notesystem.modes.check_mode.check_mode import ALL_ERRORS
from notesystem.modes.check_mode.errors.base_errors import BaseError

# TODO: change this behaviour, it could mean bugs because it gets
# assigned at the first run
CONFIG_FILE_NAME = '.notesystem'
CONFIG_FILE_LOCATIONS = [
    '~/.config/.notesystem',
]


class Config:

    def __init__(
        self,
        config_file_name: Optional[str] = CONFIG_FILE_NAME,
        config_file_locations: Optional[List[str]] = CONFIG_FILE_LOCATIONS,
    ):

        self._config_file_name = config_file_name
        self._config_file_locations = config_file_locations

        self._config_file_path: Optional[str] = None

        self.argparse_args: Optional[dict] = None
        self.OPTIONS = {
            'general': {
                'verbose': {
                    'value': None,
                    'flags': ['-v', '--verbose'],
                    'dest': 'verbose',
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
                    'dest': 'no_visual',
                    'help': 'disable visual mode (is enabled by default)',
                    'action': 'store_true',
                    'type': bool,
                    'default': True,
                    'required': False,
                },
                'config_file': {
                    'value': None,
                    'flags': ['--config-file'],
                    'dest': 'config_file',
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
                    'dest': 'watch',
                    'config_name': 'watch',
                    'help': 'enables watch mode \
                            (converts files that have changed)',
                    'type': bool,
                    'action': 'store_true',
                    'default': False,
                },
                'pandoc_args': {
                    'value': None,
                    'flags': ['--pandoc-args'],
                    'dest': 'pandoc_args',
                    'config_name': 'pandoc_args',
                    'help': "specify the arguments that need to based \
                             on to pandoc.  E.g.:  \
                             --pandoc-args='--standalone --preserve-tabs'",
                    'type': str,
                    'metavar': 'ARGS',
                    'default': None,
                },
                'pandoc_template': {
                    'value': None,
                    'flags': ['--pandoc-template'],
                    'dest': 'pandoc_args',
                    'config_name': 'pandoc_template',
                    'help': 'specify a template for pandoc to use in \
                             convertion. Default: \
                             GitHub.html5 (for md to html)',
                    'type': str,
                    'metavar': 'T',
                    # Perhaps not needed? Because it is defaulted in the code?
                    'default': None,
                },
                'to_pdf': {
                    'value': None,
                    'flags': ['--to-pdf'],
                    'dest': 'to_pdf',
                    'config_name': 'to_pdf',
                    'help': 'convert the markdown files to pdf instead of \
                             html. Note: No template is used by default.',
                    'type': bool,
                    'action': 'store_true',
                    'default': False,
                },
                'ignore_warnings': {
                    'value': None,
                    'flags': ['--ignore-warnings'],
                    'dest': 'ignore_warnings',
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
                    'metavar': 'in', 'default': None,
                },
                'fix': {
                    'value': None,
                    'flags': ['--fix', '-f'],
                    'dest': 'fix',
                    'config_name': 'fix',  # Only command line flag
                    'help': 'enables auto fixing for problems \
                            in the documents',
                    'action': 'store_true',
                    'type': bool,
                    'default': False,
                },
                'disabled_errors': [
                    self._create_option_disabled_error(error)
                    for error in ALL_ERRORS
                ],
            },
        }

    def _create_parser(self) -> argparse.ArgumentParser:

        OPTIONS = self.OPTIONS
        parser = argparse.ArgumentParser(
            prog='notesystem',
            description='A system for handing your notes for you',
        )
        # Create the convert and check parsers
        mode_parser = parser.add_subparsers(
            title='modes',
            description='choose a mode to use (required)',
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
                    opts = self._gen_argparse_args(
                        OPTIONS[section][option],
                    )
                    parser.add_argument(*opts[0], **opts[1])
            elif section == 'convert':
                for option in OPTIONS[section]:
                    opts = self._gen_argparse_args(
                        OPTIONS[section][option],
                    )
                    convert_parser.add_argument(*opts[0], **opts[1])
            elif section == 'check':
                for option in OPTIONS[section]:
                    # Handle disabled errors (is a list)
                    if isinstance(OPTIONS[section][option], list):
                        op = OPTIONS[section][option]
                        if len(op) < 1:
                            continue
                        assert 'group_name' in op[0]
                        assert 'group_desc' in op[0]
                        new_group = check_parser.add_argument_group(
                            op[0]['group_name'],
                            op[0]['group_desc'],
                        )
                        for i in OPTIONS[section][option]:
                            opts = self._gen_argparse_args(i)
                            new_group.add_argument(*opts[0], **opts[1])
                    else:
                        opts = self._gen_argparse_args(
                            OPTIONS[section][option],
                        )
                        check_parser.add_argument(*opts[0], **opts[1])
                pass
            else:
                # ERROR
                continue
        return parser

    def _create_option_disabled_error(
        self,
        error: BaseError,
    ) -> Mapping[str, Any]:
        """Helper function to create the options for the disabled errors"""
        return {
            'group_name': 'Disabled Errors',
            'group_desc': 'Using these flags you can disable checking \
                           for certain errors',
            'value': None,
            'flags': [f'--disable-{error.get_error_name()}'],
            'config_name': f'disable_{error.get_error_name().replace("-", "_")}',  # noqa: E501
            'help': f'Disable: {error.get_help_text()}',
            'action': 'store_true',
            'type': bool,
            'default': False,
            'dest': f'd-{error.get_error_name()}',
        }

    def _gen_argparse_args(self, opts: Dict) -> Tuple[List[str], Dict]:
        """Generate the arguments for ArgumentParser.add_argument()

        Returns:
            Tuple[List[str], Dict] - The first arguments (*args) and the
                                     **kwargs for add_argument()
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
                if (
                    len(flag_or_pos) >= 1 and
                    not flag_or_pos[0].startswith('-')
                ):
                    # Only add required to flags
                    # Argparse will not accept required on positional arguments
                    fn_args['required'] = opts[o]
            else:
                pass

        return (flag_or_pos, fn_args)

    def _find_config_file(self):
        """Find the config file with the higesth priority

        1. cwd
        2. ~/.config/...

        """

        if self._config_file_path:
            if os.path.isfile(self._config_file_path):
                # The config file is already found
                # probably passed using an argument
                return

        assert self._config_file_name
        current = os.path.abspath(
            os.path.join(
                os.getcwd(),
                self._config_file_name,
            ),
        )
        if os.path.isfile(current):
            self._config_file_path = current
        else:
            for path in self._config_file_locations:
                # asumes that the locations are sorted on priority
                if os.path.isfile(os.path.abspath(path)):
                    self._config_file_path = current

    def _parse_config_file(self):

        if not self._config_file_path:
            self._find_config_file()

        # There is no config file
        if (
            not self._config_file_path or
            not os.path.isfile(self._config_file_path)
        ):
            return

        cf = toml.load(self._config_file_path)

        for section in self.OPTIONS:
            if section in cf:
                for option in self.OPTIONS[section]:
                    if isinstance(self.OPTIONS[section][option], list):
                        for i, item in enumerate(
                                self.OPTIONS[section][option],
                        ):
                            for cf_option in cf[section]:
                                if cf_option == item['config_name']:
                                    self.OPTIONS[section][option][i]['value'] = cf[section][cf_option]  # noqa: E501
                        continue
                    if self.OPTIONS[section][option]['config_name']:
                        for cf_option in cf[section]:
                            if (
                                cf_option ==
                                self.OPTIONS[section][option]['config_name']
                            ):
                                self.OPTIONS[section][option]['value'] == cf[section][cf_option]  # noqa: E501

    def _parse_arguments(self):
        """Add the arguments from argparse to the options"""
        # check if the current value is in the argparse dict
        for arg in self.argparse_args:
            for section in self.OPTIONS:
                for option in self.OPTIONS[section]:
                    if isinstance(self.OPTIONS[section][option], list):
                        for i, it in enumerate(self.OPTIONS[section][option]):
                            if it['dest'] == arg:
                                if not it['value']:
                                    self.OPTIONS[section][option][i]['value'] = self.argparse_args[arg]  # noqa: E501
                        continue
                    if 'dest' in self.OPTIONS[section][option]:
                        if self.OPTIONS[section][option]['dest'] == arg:
                            # if it is but the value is empty or default
                            # skip adding the value otherwise
                            # overwrite the value
                            if (
                                self.argparse_args[arg] ==
                                self.OPTIONS[section][option]['default']
                            ):
                                # Do not write value
                                continue
                            else:
                                self.OPTIONS[section][option]['value'] = self.argparse_args[arg]  # noqa: #501
                    elif self.OPTIONS[section][option]['flags'][0] == arg:
                        # if there is no dest field it is an pos. argument
                        # therefore flags[0] has to exist
                        # and has to be the name that argparse uses
                        if (
                            self.argparse_args[arg] ==
                            self.OPTIONS[section][option]['default']
                        ):
                            continue
                        else:
                            self.OPTIONS[section][option]['value'] = self.argparse_args[arg]  # noqa: E501
        pass

    def parse(self, argv: Sequence[str]) -> dict:
        """Parse the config file and the arguments"""

        parser = self._create_parser()
        self.argparse_args = vars(parser.parse_args(argv))

        # First check for the config file
        if 'config_file' in self.argparse_args:
            self._config_file_path = self.argparse_args['config_file']

        if 'mode' not in self.argparse_args:
            parser.print_help()
            raise SystemExit(1)

        # First parse the config_file
        self._parse_config_file()
        # then parse the arguments
        # this way the arguments from the commondline overwrite the options
        # from the config file
        self._parse_arguments()

        # If the value is none set it to the default value
        for section in self.OPTIONS:
            for option in self.OPTIONS[section]:
                if isinstance(self.OPTIONS[section][option], list):
                    ls: list = self.OPTIONS[section][option]
                    for i, item in enumerate(ls):
                        if not item['value']:
                            self.OPTIONS[section][option][i]['value'] = item['default']  # noqa: E501
                    continue
                if not self.OPTIONS[section][option]['value']:
                    self.OPTIONS[section][option]['value'] = self.OPTIONS[section][option]['default']  # noqa: E501

        if self.argparse_args['mode'] == 'convert':
            return {
                'general': self.OPTIONS['general'],
                'convert': self.OPTIONS['convert'],
            }
        elif self.argparse_args['mode'] == 'check':
            return {
                'general': self.OPTIONS['general'],
                'check': self.OPTIONS['check'],
            }
        else:
            parser.print_help()
            raise SystemExit(1)
