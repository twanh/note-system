import re
from typing import List

from notesystem.modes.check_mode.errors.base_errors import BaseError


####################################
# ----- MARKDOWN ERRORS ----- #
####################################

# Gernal markdown error
class MarkdownError(BaseError):
    """An error in a markdown file that can be found by checking the markdown syntax line by line"""

    # The pattern the error can be found with
    regex_pattern: str

    fixable = False

    def validate(self, line: List[str]) -> bool:
        """Validates the line (checks if there is an error in the line)"""

    def fix(self, line: str) -> str:
        """Fixes the error on the given line and returns the correct line"""

    def is_fixable(self) -> bool:
        return self.fixable


class MathError(MarkdownError):
    """An error that occurs when math is denoted with $$

    In pandoc markdown math blocks are denoted by $$ and inline is denoted by $.
    This is not the case in some other markdown flavors (dropbox paper).
    So if this fix is applied $$ is changed to $

    """
    fixable = True
    regex_pattern = r'\$\$(.*?)\$\$'

    def validate(self, lines: List[str]) -> bool:
        """Check if there is a math error present

        Arguments:
            line {str} -- The lines to check (should only be 1 for MathError)

        Returns:
            bool -- Wheter the line is valid

        """
        if len(lines) > 1:
            raise Exception('MathError only takes one line to validate')

        matches = re.search(self.regex_pattern, lines[0])
        if not matches:
            return True
        return False

    def fix(self, line: str) -> str:
        """Fixes the math errors in the current line and returns the correct line

        Arguments:
            line {str} -- The line to fixe

        Returns:
            str -- The fixed line

        """
        return line.replace('$$', '$')

    def __str__(self):
        return 'Math Error (`$$` used)'


class SeperatorError(MarkdownError):
    """An error that is caused when there is no new line after a seperator (---)

    In pandoc markdown seperator syntax is:
    ```markdown
    ---\n
    \n
    # Header
    ```
    Common invalid syntax is:
    ```markdown
    ---\n
    # Header
    ```

    The fix for this is adding an extra new line after the seperator.

    """
    fixable = True
    regex_pattern = r'^---$'

    def validate(self, lines: List[str]) -> bool:
        """Check if there is a seperator error

        Arguments:
            lines {List[str]} -- The current line and the next line (SeperatorError needs two lines to validate)

        Returns:
            bool -- Wether the current line (lines[0]) is valid

        """

        if len(lines) != 2:
            raise Exception('SeperatorError requires 2 lines to validate')
        if not lines[0].startswith('---'):
            return True
        if lines[1] == '\n':
            return True

        return False

    def fix(self, line: str) -> str:
        """Fixes the seperator error on the current line

        Arguments:
            line {str} -- The current line

        Returns:
            str -- The fixed line

        """
        return line + '\n'

    def __str__(self):
        return 'Seperator Error (`---` used without new line)'


class TodoError(MarkdownError):
    """An error caused by invalid todo syntax

    In pandoc markdown todo item syntax is:
    ```markdown
    - [ ] This is a todo
    - [x] This todo is done
    ```
    Some markdown flavors (dropbox paper) use a very different syntax:
    ```markdown
    [ ] This is an todo
    [x] This todo is done
    ```

    The fix for this is adding the list `-` character before the the todo.
    Indentation should however be kept the same.

    """
    fixable = True
    # No regex needed
    regex_pattern = r'^\[(x|\s)\]'

    def validate(self, lines: List[str]) -> bool:
        """Check if there is a todo error

        Arguments:
            lines {List[str]} -- The line to check (only takes one)

        Raises:
            {Exception} -- If more then 1 line is given it raises an exception

        Returns:
            {bool} -- Wether the line contains a TodoError or not.

        """
        # Only one line needed
        if len(lines) != 1:
            raise Exception('TodoError requires 1 line to validate')

        # Check if the regex_pattern pattern matches the string
        # If it does not there is no TodoError present in the line
        matches = re.search(self.regex_pattern, lines[0].strip())
        if not matches:
            return True
        return False

    def fix(self, line: str) -> str:
        indent_str = line[:(len(line)-len(line.lstrip()))]
        correct_line = indent_str + '- ' + line.lstrip()
        return correct_line

    def __str__(self):
        return 'Todo Error (no `-` used in todo item)'
