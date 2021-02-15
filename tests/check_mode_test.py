import random
from typing import List

import pytest

from notesystem.modes.check_mode import SeperatorError, MathError, TodoError

################################
# --- TEST SEPERATOR ERROR --- #
################################


@pytest.mark.parametrize(
    'test_input,expected', [
        (['---\n', '# Hello world\n'], False),
        (['---\n', '\n'], True),
        (['-------------------------\n', '\n'], True),
        (['-------------------------\n', '# Hello world\n'], False),
        (['-' * random.randint(3, 50), '\n'], True),
        (['-' * random.randint(3, 50), '# Hello world\n'], False), ],
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

###########################
# --- TEST MATH ERROR --- #
###########################


@pytest.mark.parametrize(
    'test_input,expected', [
        ('There is no math it this line', True),
        ('There only is correct $math$ in this line', True),
        ('There is $$invalid$$ math in this line', False),
        ('There are multiple $$math$$ $$math$$', False),
        ('There is one $correct$ and one $$wrong$$ math block', False),
        ('Actual math: $$E=m\\cdot c^2$$', False),
        ('Actual math: $E=m\\cdot c^2$', True),
    ],
)
def test_math_error_validate(test_input, expected):
    math_error = MathError()
    assert math_error.validate([test_input]) == expected


@pytest.mark.parametrize(
    'test_input,expected', [
        (
            'There is $$invalid$$ math in this line',
            'There is $invalid$ math in this line',
        ),
        (
            'There are multiple $$math$$ $$math$$',
            'There are multiple $math$ $math$',
        ),
        (
            'There is one $correct$ and one $$wrong$$ math block',
            'There is one $correct$ and one $wrong$ math block',
        ),
        ('Actual math: $$E=m\\cdot c^2$$', 'Actual math: $E=m\\cdot c^2$'),
        # NOTE: This line is valid, but in case that a valid line is marked as
        # wrong it should not chane anything.
        ('Actual math: $E=m\\cdot c^2$', 'Actual math: $E=m\\cdot c^2$'),
    ],
)
def test_math_error_fix(test_input, expected):
    math_error = MathError()
    assert math_error.fix(test_input) == expected


def test_math_error_only_accepts_one_line():
    math_error = MathError()
    wrong_input_lines = ['$$math$$', '$$ next line $$']
    with pytest.raises(Exception):
        math_error.validate(wrong_input_lines)


###########################
# --- TEST TODO ERROR --- #
###########################
# - Dropbox paper show's todo as: `[x]` it should be: `- [x]`
@pytest.mark.parametrize(
    'test_input,expected', [
        ('[x] TODO', False),
        ('    [x] TODO', False),
        ('- [x]: Todo', True),
        ('Random string', True),
        ('\t\t [x] TODO', False),
        ('[ ] TODO', False),
        ('- [ ]', True),
        ('[ not an x or space ]', True),
    ],
)
def test_todo_error_validate(test_input, expected):
    todo_error = TodoError()
    assert todo_error.validate([test_input]) == expected


def test_todo_error_only_accepts_one_line():
    todo_error = TodoError()
    with pytest.raises(Exception):
        todo_error.validate(['line 1', 'line 2'])
