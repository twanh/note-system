import os
from unittest.mock import Mock
from unittest.mock import patch

from notesystem.modes.base_mode import ModeOptions
from notesystem.modes.search_mode import SearchMode
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


def test_split_tag_str_correctly():

    search_mode = SearchMode()
    tags = ['t1', 't2', 't3', 'ajj']
    args = {
        'pattern': 'pattern',
        'path': 'location',
        'tag_str': ' '.join(tags),
        'topic': None,
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    try:
        search_mode.start(options)
    # It will throw FileNotFoundError because location does not exist
    # but that does not matter for this test
    except FileNotFoundError:
        pass

    assert search_mode.tags == tags


def test_allow_no_tag():

    search_mode = SearchMode()
    args = {
        'pattern': 'pattern',
        'path': 'location',
        'tag_str': None,
        'topic': None,
        'case_insensitive': False,
        'title': None,
    }
    options: ModeOptions = {
        'visual': True,
        'args': args,
    }
    try:
        search_mode.start(options)
    # It will throw FileNotFoundError because location does not exist
    # but that does not matter for this test
    except FileNotFoundError:
        pass

    assert search_mode.tags == []


@patch('notesystem.modes.search_mode.SearchMode._search_dir')
def test_search_dir_is_called_when_dir_is_given(mock: Mock):

    main(['search', 'pattern', os.getcwd()])

    mock.assert_called_once_with(os.getcwd())


@patch('notesystem.modes.search_mode.SearchMode._search_file')
def test_search_file_is_called_when_file_is_given(mock: Mock):

    main(['search', 'pattern', __file__])

    mock.assert_called_once_with(__file__)
