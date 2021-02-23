import os
import shutil

from unittest.mock import Mock, patch

import pytest

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


# TODO: Test this, but with tempdirs
def test_convert_mode_calls_watcher_with_w_flag():
    """Check that watcher is called with -w (--watch) flag"""
    pass


@patch('notesystem.modes.convert_mode.ConvertMode.start')
def test_convert_mode_gets_correct_args_with_w_flag(mock_start: Mock):
    """Check that watch is True in the args when -w or --watch flag is given"""
    main(['convert', 'tests/test_documents', 'tests/out', '-w'])
    expected_args: ConvertModeArguments = {
        'in_path': 'tests/test_documents',
        'out_path': 'tests/out',
        'watch': True,
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


def test_file_not_found_error_raised_with_invalid_path():
    """Test that FileNotFoundError is raised when a invalid path is given"""
    with pytest.raises(FileNotFoundError):
        main(['convert', 'tests/test_documents/doesnotexist.md', 'test_out.html'])

# Check that custom watcher is used
# Check that convert_file writes to out path (can't be done without pandoc)
# Check that subdirectory structure is mirrored correctly
