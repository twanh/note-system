"""
Test the config

A lot of functionallity based on how the config works is already tested in
the mode specific tests.

- [ ] Test that all command line arguments are parsed correctly
- [x] Test _gen_arglarse_args
- [x] Test that the command line arguments overwrite the config file
- [x] Test that the config file is loaded correctly and the all the options in
      the config file are found
- [ ] Test that invalid options are handled in the config file
       - are ignored?
- [ ] Test that disabled errors work
- [x] Prints error when no mode is given
- [x] Test that config files are found
    - [x] From default dir
    - [ ] From the cwd
    - [ ] From command line flags?
"""
from typing import List

import py
import pytest

from notesystem.common.config import Config  # type: ignore


def test_throw_error_when_no_mode():
    """Test that SystemExit is thrown when no mode is given"""

    c = Config()
    with pytest.raises(SystemExit):
        c.parse((''))


def test_config_file_flag_sets_the_config_file(tmpdir: py.path.local):
    """Test that the --config-file sets the internal config file path"""

    config_file = tmpdir.join('test.toml')

    c = Config()
    c.parse([f'--config-file={config_file.strpath}', 'check', 'some_docs'])

    assert c._config_file_path == str(config_file.strpath)


def test_correct_mode_returned():
    """Test that the correct mode is returned"""

    c = Config()

    cov_ret = c.parse(['convert', 'in', 'uot'])
    assert 'general' in cov_ret
    assert 'convert' in cov_ret
    assert 'check' not in cov_ret

    check_ret = c.parse(['check', 'in'])
    assert 'general' in check_ret
    assert 'check' in check_ret
    assert 'convert' not in check_ret


@pytest.mark.parametrize(
    ('config_file_content', 'mode', 'section_option_value'), [
        (
            """
[general]
no_visual = true
    """, 'convert', [('general', 'no_visual', True)],
        ), (
            """
[convert]
watch = true
    """, 'convert', [('convert', 'watch', True)],
        ), (
            """
[check]
fix = true
        """, 'check', [('check', 'fix', True)],
        ), (
            """
[general]
verbose = true
no_visual = true
[convert]
watch = true
          """,
            'convert',
            [
                ('general', 'verbose', True),
                ('general', 'no_visual', True),
                ('convert', 'watch', True),
            ],
        ), (
            """
[general]
verbose = true
no_visual = true
[check]
fix = true
          """,
            'check',
            [
                ('general', 'verbose', True),
                ('general', 'no_visual', True),
                ('check', 'fix', True),
            ],
        ),
    ],
)
def test_config_file_parses_config_file(
        tmpdir: py.path.local,
        config_file_content: str,
        mode: str,
        section_option_value: List[tuple],
):
    """Test that the options set in the config file are added to the options"""
    config_file = tmpdir.join('config.toml')
    config_file.write(config_file_content)

    c = Config()
    if mode == 'convert':
        opt = c.parse(
            [f'--config-file={config_file.strpath}', mode, 'some_docs', 'out'],
        )
    else:
        opt = c.parse(
            [f'--config-file={config_file.strpath}', mode, 'some_docs'],
        )

    for sov in section_option_value:
        section = sov[0]
        option = sov[1]
        value = sov[2]
        assert opt[section][option]['value'] == value


@pytest.mark.parametrize(
    ('config_file_content', 'args', 'section_option_value'), [
        (
            """
[check]
fix=false
     """, ('cf_path', 'check', 'docs', '--fix'), (('check', 'fix', True)),
        ),
        (
            """
[convert]
watch=true
     """, ('cf_path', 'check', 'docs', '--fix'), (('check', 'fix', True)),
        ),

    ],
)
def test_commandline_arguments_overwrite_config_file(
    tmpdir: py.path.local,
    config_file_content: str,
    args: tuple,
    section_option_value: tuple,

):

    config_file = tmpdir.join('config.toml')
    config_file.write(config_file_content)

    c = Config()
    largs: List[str] = list(args)
    largs[0] = f'--config-file={config_file.strpath}'
    print(largs)
    opt = c.parse(largs)

    section = section_option_value[0]
    option = section_option_value[1]
    value = section_option_value[2]
    assert opt[section][option]['value'] == value


def test_default_config_file_locations_are_used(tmpdir: py.path.local):
    config_file = tmpdir.join('.notesystem.toml')
    config_file.write("""
[general]
no_visual=true
""")
    folder_to_check = tmpdir.strpath
    c = Config('.notesystem.toml', [folder_to_check])
    opts = c.parse(('check', 'docs'))
    assert opts['general']['no_visual']['value'] == True


@pytest.mark.parametrize(
    ('options', 'expected'), [
        (
            {
                'value': None,
                'flags': ['-v', '--verbose'],
                'dest': 'verbose',
                'config_name': 'verbose',
                'help': 'enable verbose mode (print debug output)',
                'action': 'store_true',
                'type': bool,
                'default': False,
                'required': True,
            }, (
                ['-v', '--verbose'], {
                    'action': 'store_true',
                    'required': True,
                    'default': False,
                    'dest': 'verbose',
                    'help': 'enable verbose mode (print debug output)',
                },
            ),
        ), (
            {
                'value': None,
                'flags': ['posarg1'],
                'dest': 'verbose',
                'config_name': 'verbose',
                'help': 'enable verbose mode (print debug output)',
                'type': bool,
                'default': 'def',
                'required': True,
            }, (
                ['posarg1'], {
                    'default': 'def',
                    'help': 'enable verbose mode (print debug output)',
                    'dest': 'verbose',
                },
            ),
        ),
    ],
)
def test_gen_argparse_args(options: dict, expected: tuple):
    """Test that _gen_argparse_args generates the correct arguments"""

    c = Config()

    args, kwargs = c._gen_argparse_args(options)

    assert args == expected[0]
    assert kwargs == expected[1]
