from unittest.mock import Mock
from unittest.mock import patch

import pytest

from notesystem.modes.base_mode import ModeOptions
from notesystem.modes.check_mode.check_mode import CheckMode
from notesystem.modes.check_mode.check_mode import CheckModeArgs
from notesystem.notesystem import main


def test_required_arguments():
    """Does the check mode fail without in path"""

    with pytest.raises(SystemExit):
        main(['check'])


@patch('notesystem.modes.check_mode.check_mode.CheckMode.start')
def test_check_mode_called_with_only_in_path(mock_check_mode_start: Mock):
    """Tests that the correct arguments are passed
       to check mode with only a input path
    """
    main(['check', 'tests/test_documents'])
    expected_args: CheckModeArgs = {
        'in_path': 'tests/test_documents',
        'fix': False,
    }
    expected_options: ModeOptions = {
        'visual': True,
        'args': expected_args,  # type: ignore
    }
    mock_check_mode_start.assert_called_with(expected_options)
    print(mock_check_mode_start)


@patch('notesystem.modes.check_mode.check_mode.CheckMode.start')
def test_check_mode_called_with_in_path_and_fix(mock_check_mode_start: Mock):
    """Tests that the correct arguments are passed to check mode with
       a input path and fixing enabled
    """
    main(['check', 'tests/test_documents', '-f'])
    expected_args: CheckModeArgs = {
        'in_path': 'tests/test_documents',
        'fix': True,
    }
    expected_options: ModeOptions = {
        'visual': True,
        'args': expected_args,  # type: ignore
    }
    mock_check_mode_start.assert_called_with(expected_options)
    print(mock_check_mode_start)

    main(['check', 'tests/test_documents', '--fix'])
    mock_check_mode_start.assert_called_with(expected_options)


@patch('notesystem.modes.check_mode.check_mode.CheckMode._check_dir')
def test_check_mode_checks_dir_when_given_dir(mock: Mock):
    """Test that when given a directory path, _check_dir is called"""
    main(['check', 'tests/test_documents'])
    mock.assert_called_once_with('tests/test_documents')


@patch('notesystem.modes.check_mode.check_mode.CheckMode._check_dir')
@patch('notesystem.modes.check_mode.check_mode.CheckMode._check_file')
def test_check_mode_checks_file_when_given_file(
    _check_file: Mock,
    _check_dir: Mock,
):
    """Test that when given a filepath only _check_file is called"""
    # Some parts need access to the terminal,
    # but they don'y have access so they raise value error
    # Which can be ignored
    try:
        main(['check', 'tests/test_documents/ast_error_test_1.md'])
    except ValueError:
        pass
    # _check_file should be called with the filepath
    _check_file.assert_called_with('tests/test_documents/ast_error_test_1.md')
    # Check dir should not be called
    _check_dir.assert_not_called()


# Test that fix is called
@patch('notesystem.modes.check_mode.check_mode.CheckMode._fix_doc_errors')
def test_fix_is_called_when_fix_arg_is_passed(_fix_doc_errors: Mock):
    """Test that _fix_doc_errors is called when fixing is enabled"""
    try:
        main(['check', 'tests/test_documents/ast_error_test_1.md', '-f'])
    except ValueError:
        pass
    _fix_doc_errors.assert_called()

# Test errors


def test_check_mode_raises_with_non_existing_dir_or_file():
    """Test that when a invalid path is given SystemExit is raised"""
    with pytest.raises(SystemExit):
        main(['check', 'no dir'])


def test_check_mode_check_dir_raises_with_file_and_not_existing_dir():
    """Test that _check_dir raises when the input is not a dir"""
    check_mode = CheckMode()
    # Totally invalid dir
    with pytest.raises(NotADirectoryError):
        check_mode._check_dir('not a dir')
    # With filepath
    with pytest.raises(NotADirectoryError):
        check_mode._check_dir('tests/test_documents/ast_error_test_1.md')


def test_check_mode_check_dir_returns():
    """Test that check_mode dirs returns as much doc errors as are
       present in the folder

    TODO: Make test independent of test/test_documents file amount

    """
    check_mode = CheckMode()
    errors = check_mode._check_dir('tests/test_documents')
    assert len(errors) == 3


def test_check_mode_check_file_returns():
    """Test that _check_file checks the file and returns
       errors and the correct filepath
    """
    check_mode = CheckMode()
    errors = check_mode._check_file('tests/test_documents/contains_errors.md')
    assert errors['errors'] is not None
    assert errors['file_path'] == 'tests/test_documents/contains_errors.md'


@pytest.mark.parametrize(
    'wrong,good', [
        (
            """\
[ ] Invalid todo
[x] Ivalid todo
         """, """\
- [ ] Invalid todo
- [x] Ivalid todo
         """,
        ),
        (
            """\
- [ ] Should be good
- [x] Deff is good
         """, """\
- [ ] Should be good
- [x] Deff is good
         """,
        ),
    ],
)
def test_check_mode_fix_file(tmpdir, wrong, good):

    file = tmpdir.join('test.md')
    file.write(wrong)
    check_mode = CheckMode()
    errors = check_mode._check_file(file.strpath)
    check_mode._fix_doc_errors(errors)
    c1 = file.read()
    assert c1 == good
