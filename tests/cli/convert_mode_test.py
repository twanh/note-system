import os
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


# Check that watcher is called with -w (--watch) flag
# Check that custom watcher is used
# Check that convert_dir is called when dir is passed as path
# Check that convert_file is called when file is passed as path
# Check that convert_file writes to out path (can't be done without pandoc)
# Check that subdirectory structure is mirrored correctly
# Check handling if pandoc is not available
