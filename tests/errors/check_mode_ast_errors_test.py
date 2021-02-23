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
    list_indent_error = ListIndentError()
    assert list_indent_error.validate(lines) == expected


def test_ast_error_is_fixable_return():
    ast_error = AstError()
    assert ast_error.is_fixable() == False
    ast_error.fixable = True
    assert ast_error.is_fixable() == True


def test_list_indent_non_fixable():
    list_indend_error = ListIndentError()
    with pytest.raises(Exception):
        list_indend_error.fix([])


def test_lsit_indent_str_method():
    e = ListIndentError()
    assert str(e) == 'List Indent Error (list is not properly indented)'
