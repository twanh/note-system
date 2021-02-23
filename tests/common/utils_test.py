import os

import pytest

from notesystem.common.utils import find_all_md_files


def test_find_all_md_files():

    files = find_all_md_files('tests/test_documents')
    assert len(files) == 3


def test_find_all_md_files_raises_when_dir_does_not_exist():
    with pytest.raises(NotADirectoryError):
        files = find_all_md_files('nodir')
