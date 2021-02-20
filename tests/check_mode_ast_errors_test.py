import pytest

from notesystem.modes.check_mode.errors.ast_errors import *

##################################
# --- TEST LIST INDENT ERROR --- #
##################################


@pytest.mark.parametrize(
    'test_file,expected', [
        # Invalid doc
        ('tests/test_documents/ast_error_test_1.md', False),
        # Valid doc
        ('tests/test_documents/ast_error_test_2.md', True),
    ],
)
def test_list_indent_validate(test_file, expected):
    with open(test_file) as test_file:
        lines = test_file.readlines()
    list_index_error = ListIndentError()
    assert list_index_error.validate(lines) == expected
