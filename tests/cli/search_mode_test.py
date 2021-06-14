from unittest.mock import Mock
from unittest.mock import patch

from notesystem.modes.base_mode import ModeOptions
from notesystem.notesystem import main


@patch('notesystem.modes.search_mode.SearchMode._run')
def test_search_mode_called(run_mock: Mock):
    main(['search', 'pattern', 'location'])
    run_mock.assert_called_once()


@patch('notesystem.modes.search_mode.SearchMode.start')
def test_search_mode_called_with_correct_args_tags(start_mock: Mock):

    tag_str = 'hi'
    main(['search', 'pattern', 'location', '--tags', tag_str])

    expected_args = {
        'pattern': 'pattern',
        'path': 'location',
        'tag_str': tag_str,
        'topic': None,
        'case_insensitive': False,
        'title': None,
    }

    expected_options: ModeOptions = {
        'visual': True,
        'args': expected_args,
    }

    start_mock.assert_called_with(expected_options)
