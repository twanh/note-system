import os
import shutil
import subprocess
from unittest.mock import Mock, patch, MagicMock

import pytest
import py

from notesystem.notesystem import main
from notesystem.modes.base_mode import ModeOptions
from notesystem.notesystem import ConvertMode, ConvertModeArguments


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
        },
    }
    expected_options: ModeOptions = {
        'visual': True,
        'args': expected_args,  # type: ignore
    }
    mock_convert_mode.assert_called_once_with(expected_options)


@patch('shutil.which')
def test_convert_mode_checks_pandoc_install(mock_which: Mock):
    """Check that shutil.which is called to check if pandoc is installed when convert mode is started"""
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
        },
    }
    expected_options: ModeOptions = {
        'visual': True,
        'args': expected_args,  # type: ignore
    }
    mock_start.assert_called_with(expected_options)


@patch('notesystem.modes.convert_mode.ConvertMode._convert_dir')
def test_convert_dir_is_called_when_in_path_is_dir(convert_dir_mock: Mock):
    """Test that _convert_dir is called when the given input path is a folder"""
    # NOTE: No files should be written to test_out/ folder because convert_dir is mocked
    main(['convert', 'tests/test_documents', 'test_out'])
    convert_dir_mock.assert_called_with('tests/test_documents', 'test_out')


@patch('notesystem.modes.convert_mode.ConvertMode._convert_file')
def test_convert_file_is_called_when_in_path_is_file(convert_file_mock: Mock):
    """Test that _convert_file is called when the given input path is a file"""
    # NOTE: No files should be written to test_out/ folder because convert_dir is mocked
    main(['convert', 'tests/test_documents/contains_errors.md', 'test_out.html'])
    convert_file_mock.assert_called_with(
        'tests/test_documents/contains_errors.md', 'test_out.html',
    )


@patch('subprocess.run')
def test_pandoc_command_with_correct_args_options(run_mock: Mock):
    """Test that pandoc is called with the correct filenames and flags"""

    in_file = 'tests/test_documents/ast_error_test_1.md'
    out_file = 'test/test_documents/out.html'
    pd_args = '--preserve-tabs --standalone'
    pd_command = f'pandoc {in_file} -o {out_file} --template GitHub.html5 --mathjax {pd_args}'

    main(['convert', in_file, out_file, f'--pandoc-args={pd_args}'])
    run_mock.assert_called_once_with(
        pd_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


@patch('subprocess.run')
def test_pandoc_command_with_correct_args_tempalte(run_mock: Mock):
    """Test that pandoc is called with the correct filenames and flags"""

    in_file = 'tests/test_documents/ast_error_test_1.md'
    out_file = 'test/test_documents/out.html'
    pd_template = 'easy_template.html'
    pd_command = f'pandoc {in_file} -o {out_file} --template {pd_template} --mathjax '

    main(['convert', in_file, out_file, f'--pandoc-template={pd_template}'])
    run_mock.assert_called_once_with(
        pd_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


# @pytest.mark.skipif(os.environ.get('CI') == 'true', reason='Github Actions does not play well with tmpdirs')
# def test_convert_file_converts_file(tmpdir: py.path.local):
#     """Test that convert file convert the file correctly using pandoc with default GitHub.html5 template"""
#     content = """\
# # Heading 1

# Paragrpah text
#         """
#     file = tmpdir.join('test.md')
#     out_file = tmpdir.join('test.html')
#     pandoc_out = tmpdir.join('pd.html')
#     file.write(content)

#     print(f"OSSS::::::: {os.environ.get('CI')}")
#     conv_mode = ConvertMode()
#     conv_mode._convert_file(file.strpath, out_file.strpath)

#     pd_command = f'pandoc {file.strpath} -o {pandoc_out.strpath} --template GitHub.html5 --mathjax'
#     subprocess.run(
#         pd_command, shell=True,
#         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
#     )

#     assert out_file.read() == pandoc_out.read()


def test_handle_subprocess_error(capsys: pytest.CaptureFixture):
    """Test that subprocess.CalledProcessError is handled and program quits"""
    mock = MagicMock(side_effect=subprocess.CalledProcessError(1, cmd='Test'))
    with patch('subprocess.run', mock) as run_mock:
        with pytest.raises(SystemExit):
            main(['convert', 'tests/test_documents/contains_errors.md', 'out.html'])
            run_mock.assert_called()


def test_file_not_found_error_raised_with_invalid_path():
    """Test that FileNotFoundError is raised when a invalid path is given"""
    with pytest.raises(FileNotFoundError):
        main(['convert', 'tests/test_documents/doesnotexist.md', 'test_out.html'])


# _convert_file is mocked here, so that no actual convertion happens and watch mode is still called
@patch('notesystem.modes.convert_mode.ConvertMode._convert_file')
@patch('notesystem.modes.convert_mode.ConvertMode._start_watch_mode')
def test_watcher_is_called_when_watch_mode(start_watch_mode_mock: Mock, _):
    """Test that _start_watch_mode_is_called"""
    main(['convert', 'tests/test_documents/contains_errors.md', 'test_out.html', '-w'])
    expected_args: ConvertModeArguments = {
        'in_path': 'tests/test_documents/contains_errors.md',
        'out_path': 'test_out.html',
        'watch': True,
        'pandoc_options': {
            'template': None,
            'arguments': None,
        },
    }
    start_watch_mode_mock.assert_called_once_with(expected_args)

# Check that custom watcher is used
# Check that convert_file writes to out path (can't be done without pandoc)
# Check that subdirectory structure is mirrored correctly
