import random
from typing import List

import pytest

from notesystem.modes.check_mode import SeperatorError


@pytest.mark.parametrize(
    'test_input,expected', [
        (['---\n', '# Hello world\n'], False),
        (['---\n', '\n'], True),
        (['-------------------------\n', '\n'], True),
        (['-------------------------\n', '# Hello world\n'], False),
        (['-' * random.randint(3, 50), '\n'], True),
        (['-' * random.randint(3, 50), '# Hello world\n'], False),
    ],
)
def test_seperator_error_validate(test_input: List[str], expected: bool):
    sep_err = SeperatorError()
    assert sep_err.validate(test_input) == expected


@pytest.mark.parametrize(
    'test_input,expected', [
        ('---\n', '---\n\n'),
        ('-'*9 + '\n', '-'*9 + '\n\n'),
    ],
)
def test_seperator_error_fix(test_input: str, expected: str):
    sep_err = SeperatorError()
    assert sep_err.fix(test_input) == expected


def test_seperator_error_throws():
    sep_err = SeperatorError()
    lines = ['---', '\n', '']
    with pytest.raises(Exception):
        sep_err.validate(lines)
