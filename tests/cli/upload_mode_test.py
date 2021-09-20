"""Test the upload mode

TODO:
- Test for FileNotFound
- Test for non unicode characters
- Mock all requests to the server
"""
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from notesystem.modes.base_mode import ModeOptions
from notesystem.modes.upload_mode import UploadModeArguments
from notesystem.notesystem import main


def test_upload_mode_required_args():

    with pytest.raises(SystemExit):
        main(['upload'])


@patch('notesystem.modes.upload_mode.UploadMode.start')
def test_upload_mode_is_called_with_correct_args(start_mock: Mock):

    main(('upload', 'notes/', 'https://test.com/'))

    expected_args: UploadModeArguments = {
        'path': 'notes/',
        'url': 'https://test.com/',
        'username': None,
        'save_credentials': False,
    }
    expected_options: ModeOptions = {
        'visual': True,
        'args': expected_args,  # type:ignore
    }

    start_mock.assert_called_once_with(expected_options)
