import os
from typing import List

import pytest
import py

from notesystem.common.utils import find_all_md_files


def test_find_all_md_files():

    files = find_all_md_files('tests/test_documents')
    assert len(files) == 3


def test_find_all_md_files_only_returns_md_files(tmpdir: py.path.local):
    files_to_make = 5
    # Create some markdown and non markdown files
    for i in range(0, files_to_make):
        file = tmpdir.join(f'test{i}.md')
        file.write('# Heading 1')
    not_a_md_file = tmpdir.join('notmd.html')
    not_a_md_file.write('<h1>no markdown here</h1>')

    found_files = find_all_md_files(tmpdir.strpath)

    assert len(found_files) == files_to_make


def test_find_all_md_files_raises_when_dir_does_not_exist():
    with pytest.raises(NotADirectoryError):
        files = find_all_md_files('nodir')
