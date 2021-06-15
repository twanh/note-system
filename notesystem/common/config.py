# type: ignore
"""
Provides the configuration functionality for notesystem

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

CONFIG_FILE_NAME = '.notesystem'
CONFIG_FILE_LOCATIONS = [
    os.path.expanduser('~'),
    os.path.expanduser('~/.config/'),
]


class Config:

    def __init__(
        self,
        config_file_name: Optional[str] = None,
        config_file_locations: Optional[List[str]] = None,
    ):
        """Initialize the config

        Arguments:
            config_file_name {Optional[str]} - The name of the config file
            config_file_locations {Optional[List[str]]} - The locations where
                to look for the config file

        """

        self._config_file_name = config_file_name or CONFIG_FILE_NAME
        self._config_file_locations = (
            config_file_locations or CONFIG_FILE_LOCATIONS
        )

        # The actual path to the config file that will be used.
        self._config_file_path: Optional[str] = None

        # The arugments parsed by argparse
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
                'no_visual': {
                    'value': None,
                    'flags': ['--no-visual'],
                    'config_name': 'no_visual',
                    'dest': 'no_visual',
                    'help': 'disable visual mode (is enabled by default)',
                    'action': 'store_true',
                    'type': bool,
                    'default': False,
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
                    'dest': 'template',
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
                    'metavar': 'in',
                    'default': None,
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
            'search': {
                'pattern': {
                    'value': None,
                    'flags': ['pattern'],
                    'help': 'the pattern to search for',
                    'required': True,
                    'default': None,
                    'config_name': None,
                },
                'path': {
                    'value': None,
                    'flags': ['path'],
                    'help': 'the path to search in',
                    'default': None,
                },
                'tags': {
                    'value': None,
                    'flags': ['--tags'],
                    'default': None,
                    'dest': 'tags',
                    'required': False,
                    'help': 'a space seperated list of tags to search for',
                    'type': str,
                },
                'topic': {
                    'value': None,
                    'flags': ['--topic'],
                    'default': None,
                    'dest': 'topic',
                    'required': False,
                    'help': 'the topic (or subject) defined in the\
                             frontmatter to search for',
                    'type': str,
                },
                'title': {
                    'value': None,
                    'flags': ['--title'],
                    'default': None,
                    'dest': 'title',
                    'required': False,
                    'help': 'the title defined in the\
                             frontmatter to search for',
                    'type': str,
                },
                'case_insensitive': {
                    'value': None,
                    'flags': ['-i', '--insensitive'],
                    'dest': 'case_insensitive',
                    'default': False,
                    'action': 'store_true',
                    'required': False,
                    'help': 'make the search case insensitive',
                    'type': bool,
                },
            },
        }

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser based on self.OPTIONS

        Returns:
            {argparse.ArgumentParser} - The (created) argument parser

        """

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

        search_parser = mode_parser.add_parser(
            'search',
            help='search through notes',
        )
        search_parser.set_defaults(mode='search')

        # Parse the OPTIONS dict and create the argparser
        for section in self.OPTIONS:
            if section == 'general':
                # Create the main parser
                for option in self.OPTIONS[section]:
                    opts = self._gen_argparse_args(
                        self.OPTIONS[section][option],
                    )
                    parser.add_argument(*opts[0], **opts[1])
            elif section == 'convert':
                for option in self.OPTIONS[section]:
                    opts = self._gen_argparse_args(
                        self.OPTIONS[section][option],
                    )
                    convert_parser.add_argument(*opts[0], **opts[1])
            elif section == 'check':
                for option in self.OPTIONS[section]:
                    # TODO: Should this only be in check?
                    #       Currenlty only the disabled_errors needs this
                    #       but in the future more options might?
                    # Handle disabled errors (is a list)
                    if isinstance(self.OPTIONS[section][option], list):
                        op = self.OPTIONS[section][option]
                        if len(op) < 1:
                            continue
                        assert 'group_name' in op[0], f'No group_name in {op}'
                        assert 'group_desc' in op[0], f'No group_desc in {op}'
                        new_group = check_parser.add_argument_group(
                            op[0]['group_name'],
                            op[0]['group_desc'],
                        )
                        for i in self.OPTIONS[section][option]:
                            opts = self._gen_argparse_args(i)
                            new_group.add_argument(*opts[0], **opts[1])
                    else:
                        args, kwargs = self._gen_argparse_args(
                            self.OPTIONS[section][option],
                        )
                        check_parser.add_argument(*args, **kwargs)
                pass
            elif section == 'search':
                for option in self.OPTIONS[section]:
                    sargs, kwargs = self._gen_argparse_args(
                        self.OPTIONS[section][option],
                    )
                    search_parser.add_argument(*sargs, **kwargs)
            else:
                # This should never be reached...
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
        # TODO: Perhaps a better way to do this always add the option
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
                    flag_or_pos[0].startswith('-')
                ):
                    # Only add required to flags
                    # Argparse will not accept required on positional arguments
                    fn_args['required'] = opts[o]
            else:
                pass

        return (flag_or_pos, fn_args)

    def _find_config_file(self):
        """Find the config file with the highest priority

        Possible locations are based on self._config_file_locations.

        Config file in the current working directory (from where the notesystem
        command is executed) has the highest priority.

        When the config file is set using a command line argument it will
        be used instead of any other config file.

        """

        if self._config_file_path:
            if os.path.isfile(self._config_file_path):
                # The config file is already found
                return

        assert self._config_file_name

        # Look for the config file in the cwd (pwd)
        current = os.path.abspath(
            os.path.join(
                os.getcwd(),
                self._config_file_name,
            ),
        )
        if os.path.isfile(current):
            self._config_file_path = current
        else:
            # Look through all possible locations
            # Note: assumes that the locations are sorted on priority
            for _path in self._config_file_locations:
                full_path = os.path.join(
                    os.path.abspath(_path), self._config_file_name,
                )
                if os.path.isfile(full_path):
                    self._config_file_path = full_path
                    return

    def _parse_config_file(self):
        """Parse the config file and add all set options to self.OPTIONS

        The config file is parsed based on the section in
        the self.OPTIONS dict. Every section has multiple options and if the
        options has a `config_name` key the config file is checked to see
        if the current `config_name` is in the config file. If it is it's
        value is written to the `value` key of the current option.

        """

        if not self._config_file_path:
            self._find_config_file()

        # There is no config file (which is totally possible)
        if (
            not self._config_file_path or
            not os.path.isfile(self._config_file_path)
        ):
            return

        cf = toml.load(self._config_file_path)

        for section in self.OPTIONS:
            if section in cf:
                for option in self.OPTIONS[section]:
                    # Some options (currently only disabled_errors) are a list
                    # if they are loop through the list and 'treat' every item
                    # as if they were an option.
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
                                value = cf[section][cf_option]
                                self.OPTIONS[section][option]['value'] = value

    def _parse_arguments(self):
        """Add the arguments from argparse to the options"""

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
                        # if there is no dest field it is a positional argument
                        # therefore flags[0] has to exist
                        # and has to be the name that argparse uses
                        if (
                            self.argparse_args[arg] ==
                            self.OPTIONS[section][option]['default']
                        ):
                            continue
                        else:
                            self.OPTIONS[section][option]['value'] = self.argparse_args[arg]  # noqa: E501

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
        # this way the arguments from the commandline overwrite the options
        # from the config file
        self._parse_arguments()

        # If the value is None set it to the default value
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

        # Create the return value based on the mode
        # only one mode can be used at once so only return the active mode
        # this allows the main program to see which mode is in the options
        # and activate that mode
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
        elif self.argparse_args['mode'] == 'search':
            return {
                'general': self.OPTIONS['general'],
                'search': self.OPTIONS['search'],
            }
        else:
            # Just for form... This code should never get executed
            parser.print_help()
            raise SystemExit(1)
