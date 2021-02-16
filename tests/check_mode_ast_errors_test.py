import pytest

from notesystem.modes.check_mode.errors.ast_errors import *

##################################
# --- TEST LIST INDENT ERROR --- #
##################################


@pytest.mark.parametrize(
    'test_input,expected', [
        (['# Not a list', '\t- indented List'], False),
        (['- I am a list', '\t- indented List'], True),
        (['# Not a list', '- not indented List'], True),
        (['\n', '\t- I AM LIST\n'], False),
        (['This should be a codeblock\n', '```python\n'], True),
        (['```sql\n', '-- This is actually a comment'], True),
    ],
)
def test_list_index_validate(test_input, expected):
    list_index_error = ListIndentError()
    assert list_index_error.validate(test_input) == expected
