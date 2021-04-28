import subprocess
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from py.path import local as Path

from notesystem.modes.base_mode import ModeOptions
from notesystem.modes.convert_mode import ConvertModeArguments
from notesystem.notesystem import main


def test_convert_mode_required_argds():
    """Test that convert mode raises when not given the correct arguments"""
    with pytest.raises(SystemExit):
        main(['convert'])
    with pytest.raises(SystemExit):
        main(['convert', 'indir'])


@patch('notesystem.modes.convert_mode.ConvertMode.start')
def test_convert_mode_called_correct_args(mock_convert_mode: Mock):
    """Test that convert mode is called with the correct arugments"""
    main(['convert', 'tests/test_documents', 'tests/out'])
    expected_args: ConvertModeArguments = {
        'in_path': 'tests/test_documents',
        'out_path': 'tests/out',
        'watch': False,
        'pandoc_options': {
            'template': None,
            'arguments': None,
            'output_format': 'html',
            'ignore_warnings': False,
        },
    }
    expected_options: ModeOptions = {
        'visual': True,
        'args': expected_args,  # type: ignore
    }
    mock_convert_mode.assert_called_once_with(expected_options)


@patch('shutil.which')
def test_convert_mode_checks_pandoc_install(mock_which: Mock):
    """Check that shutil.which is called to check if pandoc is installed
        when convert mode is started
    """
    # Test that error is raised when pandoc is not installed
    mock_which.return_value = None
    with pytest.raises(SystemExit):
        main(['convert', 'in', 'out'])
    # Check that which is aclled
    mock_which.assert_called_once_with('pandoc')
    # Set mock value to be a str, meaning pandoc is installed
    # So no error should be raised
    mock_which.return_value = '~/bin/pandoc'
    try:
        main(['convert', 'in', 'out'])
    except FileNotFoundError:
        # FileNotFoundError is expected, since no valid path is given
        pass
    mock_which.assert_called_with('pandoc')


@patch('notesystem.modes.convert_mode.ConvertMode.start')
def test_convert_mode_gets_correct_args_with_w_flag(mock_start: Mock):
    """Check that watch is True in the args when -w or --watch flag is given"""
    main(['convert', 'tests/test_documents', 'tests/out', '-w'])
    expected_args: ConvertModeArguments = {
        'in_path': 'tests/test_documents',
        'out_path': 'tests/out',
        'watch': True,
        'pandoc_options': {
            'template': None,
            'arguments': None,
            'output_format': 'html',
            'ignore_warnings': False,
        },
    }
    expected_options: ModeOptions = {
        'visual': True,
        'args': expected_args,  # type: ignore
    }
    mock_start.assert_called_with(expected_options)


@patch('notesystem.modes.convert_mode.ConvertMode._convert_dir')
def test_convert_dir_is_called_when_in_path_is_dir(convert_dir_mock: Mock):
    """Test that _convert_dir is called when the given
       input path is a folder
    """
    # NOTE: No files should be written to test_out/ folder
    # because convert_dir is mocked
    main(['convert', 'tests/test_documents', 'test_out'])
    convert_dir_mock.assert_called_with('tests/test_documents', 'test_out')


@patch('notesystem.modes.convert_mode.ConvertMode._convert_file')
def test_convert_file_is_called_when_in_path_is_file(convert_file_mock: Mock):
    """Test that _convert_file is called when the given input path is a file"""

    main([
        'convert',
        'tests/test_documents/contains_errors.md',
        'test_out.html',
    ])
    convert_file_mock.assert_called_with(
        'tests/test_documents/contains_errors.md', 'test_out.html',
    )


@patch('subprocess.run')
def test_pandoc_command_with_correct_args_options(run_mock: Mock):
    """Test that pandoc is called with the correct filenames and flags"""

    in_file = 'tests/test_documents/ast_error_test_1.md'
    out_file = 'test/test_documents/out.html'
    pd_args = '--preserve-tabs --standalone'
    pd_command = f'pandoc {in_file} -o {out_file} --template GitHub.html5 --mathjax {pd_args} -t html'  # noqa: E501

    main(['convert', in_file, out_file, f'--pandoc-args={pd_args}'])

    run_mock.assert_called_once_with(
        pd_command,
        shell=True,
        capture_output=True,
    )


@patch('subprocess.run')
def test_pandoc_command_with_correct_args_template(run_mock: Mock):
    """Test that pandoc is called with the correct filenames and flags"""

    in_file = 'tests/test_documents/ast_error_test_1.md'
    out_file = 'test/test_documents/out.html'
    pd_template = 'easy_template.html'
    pd_command = f'pandoc {in_file} -o {out_file} --template {pd_template} --mathjax  -t html'  # noqa: E501

    main(['convert', in_file, out_file, f'--pandoc-template={pd_template}'])
    run_mock.assert_called_once_with(
        pd_command,
        shell=True,
        capture_output=True,
    )


@patch('subprocess.run')
def test_pandoc_command_with_correct_args_template_None(run_mock: Mock):
    """Test that when the pandoc-template flag is set to None
       no template is used.
    """

    in_file = 'tests/test_documents/ast_error_test_1.md'
    out_file = 'test/test_documents/out.html'
    pd_command = f'pandoc {in_file} -o {out_file}  --mathjax  -t html'  # noqa: E501

    main(['convert', in_file, out_file, '--pandoc-template=None'])
    run_mock.assert_called_once_with(
        pd_command,
        shell=True,
        capture_output=True,
    )


@patch('subprocess.run')
def test_pandoc_command_with_correct_file_output(run_mock: Mock):
    """Test that pandoc is called with the -t pdf when --to-pdf
       is specified.
    """

    in_file = 'tests/test_documents/ast_error_test_1.md'
    out_file = 'test/test_documents/out.pdf'
    pd_command = f'pandoc {in_file} -o {out_file}  --mathjax  -t pdf'  # noqa: E501

    main(['convert', in_file, out_file, '--to-pdf'])
    run_mock.assert_called_once_with(
        pd_command,
        shell=True,
        capture_output=True,
    )


@patch('subprocess.run')
def test_pandoc_command_with_correct_file_output_with_template(run_mock: Mock):
    """Test that pandoc is called with the correct filenames and flags when
       --to-pdf is passed and also a template is specified.
    """

    in_file = 'tests/test_documents/ast_error_test_1.md'
    out_file = 'test/test_documents/out.pdf'
    pd_template = 'eisvogel.latex'
    pd_command = f'pandoc {in_file} -o {out_file} --template {pd_template} --mathjax  -t pdf'  # noqa: E501

    main([
        'convert', in_file, out_file,
        f'--pandoc-template={pd_template}', '--to-pdf',
    ])
    run_mock.assert_called_once_with(
        pd_command,
        shell=True,
        capture_output=True,
    )


@patch('subprocess.run')
def test_pandoc_command_with_changed_to_pdf_with_html_filename(run_mock: Mock):
    """ Test that the output file name extension is changed to
        .pdf when .html is given
    """

    in_file = 'tests/test_documents/ast_error_test_1.md'
    # Outfile is html file but should be .pdf beause --to-pdf passed
    out_file = 'test/test_documents/out.html'
    out_file_correct = 'test/test_documents/out.pdf'
    pd_command = f'pandoc {in_file} -o {out_file_correct}  --mathjax  -t pdf'  # noqa: E501

    main(['convert', in_file, out_file, '--to-pdf'])
    run_mock.assert_called_once_with(
        pd_command,
        shell=True,
        capture_output=True,
    )


@patch('subprocess.run')
def test_pandoc_command_with_correct_args_template_and_options(run_mock: Mock):
    """Test that pandoc is called with the correct filenames and
       flags when a custom template is used and extra arguments are given
    """

    in_file = 'tests/test_documents/ast_error_test_1.md'
    out_file = 'test/test_documents/out.html'
    pd_template = 'easy_template.html'
    pd_args = '--preserve-tabs --standalone'
    pd_command = f'pandoc {in_file} -o {out_file} --template {pd_template} --mathjax {pd_args} -t html'  # noqa: E501

    main([
        'convert', in_file, out_file,
        f'--pandoc-template={pd_template}', f'--pandoc-args={pd_args}',
    ])
    run_mock.assert_called_once_with(
        pd_command,
        shell=True,
        capture_output=True,
    )


@pytest.mark.parametrize(
    'not_allowed_arg', [
        '-o',
        '--to',
        '--from',
        '--mathjax'
        '--template',
    ],
)
def test_convert_file_raises_with_not_allowed_pandoc_args(not_allowed_arg):
    """Test that when there are not allowed arguments given
       as --pandoc-args pararameters _convert_file raises SystemExit(1) error
    """

    with pytest.raises(SystemExit):
        main([
            'convert', 'tests/test_documents/contains_errors.md',
            'output.html', f'--pandoc-args={not_allowed_arg}',
        ])


def test_handle_subprocess_error():
    """Test that subprocess.CalledProcessError is handled and program quits"""
    mock = MagicMock(side_effect=subprocess.CalledProcessError(1, cmd='Test'))
    with patch('subprocess.run', mock) as run_mock:
        with pytest.raises(SystemExit):
            main([
                'convert',
                'tests/test_documents/contains_errors.md',
                'out.html',
            ])
            run_mock.assert_called()


def test_file_not_found_error_raised_with_invalid_path():
    """Test that FileNotFoundError is raised when a invalid path is given"""
    with pytest.raises(FileNotFoundError):
        main([
            'convert',
            'tests/test_documents/doesnotexist.md',
            'test_out.html',
        ])


# _convert_file is mocked here
# so that no actual convertion happens and watch mode is still called
@patch('notesystem.modes.convert_mode.ConvertMode._convert_file')
@patch('notesystem.modes.convert_mode.ConvertMode._start_watch_mode')
def test_watcher_is_called_when_watch_mode(start_watch_mode_mock: Mock, _):
    """Test that _start_watch_mode_is_called"""
    main([
        'convert',
        'tests/test_documents/contains_errors.md',
        'test_out.html',
        '-w',
    ])
    expected_args: ConvertModeArguments = {
        'in_path': 'tests/test_documents/contains_errors.md',
        'out_path': 'test_out.html',
        'watch': True,
        'pandoc_options': {
            'template': None,
            'arguments': None,
            'output_format': 'html',
            'ignore_warnings': False,
        },
    }
    start_watch_mode_mock.assert_called_once_with(expected_args)


def test_pandoc_warnings_are_printed(capsys, tmpdir: Path):
    """Test that when pandoc prints a warning the warning is also printed
       out to the user.
    """
    outfile_path = tmpdir.join('outfile.html')

    main([
        'convert',
        'tests/test_documents/contains_errors.md',
        str(outfile_path),
        # Standalone raises an warning
        '--pandoc-args="--standalone"',
        # Default template not installed in CI.
        # Therefor not using a template (because throws error)
        '--pandoc-template=None',
    ])

    captured = capsys.readouterr()
    assert 'PANDOC WARNING' in captured.out
    assert '[WARNING]' in captured.out


def test_pandoc_warnings_are_not_printed_with_ignore_warnings_flag(
    capsys,
    tmpdir: Path,
):
    """Test that when pandoc prints a warning the warning is is not printed
       when the `--ignore-warnings` flag is passed.
    """
    outfile_path = tmpdir.join('outfile.html')

    main([
        'convert',
        # Next to the fact that it contains errors, it also has
        # no title, which means that pandoc will throw a warning
        'tests/test_documents/contains_errors.md',
        str(outfile_path),
        # Standalone raises an warning
        '--pandoc-args="--standalone"',
        # Default template not installed in CI.
        # Therefor not using a template (because throws error)
        '--pandoc-template=None',
        '--ignore-warnings',
    ])

    captured = capsys.readouterr()
    assert 'PANDOC WARNING' not in captured.out
    assert '[WARNING]' not in captured.out


def test_pandoc_errors_are_printed(capsys, tmpdir: Path):
    """Test that when pandoc prints an error the error is also printed
       out to the user.
    """
    outfile_path = tmpdir.join('outfile.html')

    main([
        'convert',
        # Next to the fact that it contains errors, it also has
        # no title, which means that pandoc will throw a warning
        'tests/test_documents/contains_errors.md',
        # Trying to use a non-existing template
        # should throw an error
        '--pandoc-template="noexisting_template.html"',
        str(outfile_path),
    ])

    captured = capsys.readouterr()
    assert 'PANDOC ERROR' in captured.out
    assert 'Could not convert' in captured.out


def test_pandoc_errors_are_printed_with_ignore_warnings_flag(
    capsys,
    tmpdir: Path,
):
    """Test that when pandoc prints an error the error is also printed
       out to the user.
    """
    outfile_path = tmpdir.join('outfile.html')

    main([
        'convert',
        # Next to the fact that it contains errors, it also has
        # no title, which means that pandoc will throw a warning
        'tests/test_documents/contains_errors.md',
        # Trying to use a non-existing template
        # should throw an error
        '--pandoc-template="noexisting_template.html"',
        str(outfile_path),
        '--ignore-warnings',
    ])

    captured = capsys.readouterr()
    assert 'PANDOC ERROR' in captured.out
    assert 'Could not convert' in captured.out

# Check that custom watcher is used
# Check that convert_file writes to out path (can't be done without pandoc)
# Check that subdirectory structure is mirrored correctly
