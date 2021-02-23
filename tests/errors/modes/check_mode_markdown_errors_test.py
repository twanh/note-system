import random
from typing import List

import pytest

from notesystem.modes.check_mode.errors.markdown_errors import *

################################
# --- TEST BASE ERROR --- #
################################


def test_markdown_error_returns_fixable():
    md_error = MarkdownError()
    assert md_error.is_fixable() == False
    md_error.fixable = True
    assert md_error.fixable == True

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
    assert sep_err.fix([test_input])[0] == expected


def test_seperator_error_validate_throws():
    sep_err = SeperatorError()
    lines = ['---', '\n', '']
    with pytest.raises(Exception):
        sep_err.validate(lines)


def test_seperator_error_fix_throws():
    sep_err = SeperatorError()
    lines = ['---', '\n', '']
    with pytest.raises(Exception):
        sep_err.fix(lines)


def test_seperator_error_str():
    sep_err = SeperatorError()
    assert str(sep_err) == 'Seperator Error (`---` used without new line)'


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
    assert math_error.fix([test_input])[0] == expected


def test_math_error_validate_only_accepts_one_line():
    math_error = MathError()
    wrong_input_lines = ['$$math$$', '$$ next line $$']
    with pytest.raises(Exception):
        math_error.validate(wrong_input_lines)


def test_math_error_fix_only_accepts_one_line():
    math_error = MathError()
    wrong_input_lines = ['$$math$$', '$$ next line $$']
    with pytest.raises(Exception):
        math_error.fix(wrong_input_lines)


def test_math_error_str():
    math_error = MathError()
    assert str(math_error) == 'Math Error (`$$` used)'


###########################
# --- TEST TODO ERROR --- #
###########################

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


@pytest.mark.parametrize(
    'test_input,expected', [
        ('[x] TODO', '- [x] TODO'),
        (' ' * 3 + '[x] TODO', ' ' * 3 + '- [x] TODO'),
        ('\t\t[x] TODO', '\t\t- [x] TODO'),
        ('[ ] TODO', '- [ ] TODO'),
    ],
)
def test_todo_error_fix(test_input, expected):
    todo_error = TodoError()
    assert todo_error.fix([test_input])[0] == expected


def test_todo_error_fix_only_accepts_one_line():
    todo_error = TodoError()
    wrong_input = ['', '']
    with pytest.raises(Exception):
        todo_error.fix(wrong_input)


def test_todo_error_str():
    todo_error = TodoError()
    assert str(todo_error) == 'Todo Error (no `-` used in todo item)'
