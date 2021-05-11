from unittest.mock import Mock
from unittest.mock import patch

from notesystem.notesystem import main


@patch('notesystem.modes.search_mode.SearchMode._run')
def test_search_mode_called(run_mock: Mock):
    main(['search', 'search_term'])
    run_mock.assert_called_once()
