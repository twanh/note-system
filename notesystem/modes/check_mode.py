import os
import re
import abc
from typing import TypedDict, List, Dict, Tuple, Union

import mistune

from notesystem.modes.base_mode import BaseMode

####################################
# ----- MARKDOWN ERRORS ----- #
####################################


class MarkdownError(abc.ABC):
    """An error in a markdown file"""
    # Wether the error (type) is fixable
    fixable: bool
    # The pattern the error can be found with
    regex_pattern: str

    @abc.abstractclassmethod
    def validate(self, line: List[str]) -> bool:
        """Validates the line (checks if there is an error in the line)"""

    @abc.abstractclassmethod
    def fix(self, line: str) -> str:
        """Fixes the error on the given line and returns the correct line"""


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


class ListIndentError(MarkdownError):
    fixable = True
    regex_pattern = ''

    def validate(self, lines: List[str]) -> bool:
        """Check if there is a ListIndentError present in the given lines

        Arguments:
            lines {List[str]} -- The lines to check (should be two for ListIndentError)

        Raises:
            {Exception} -- When any other amount of lines then 2 is given an exception is raised

        Returns:
            {bool} -- Wether the lines are valid

        """

        if len(lines) != 2:
            raise Exception('ListIndentError needs two lines to validate')

        # It is easier to (accuractly) detect a ListIndentError using the ast and reasoning about that
        # then using a regex that matches any indented list
        create_ast = mistune.create_markdown(
            escape=False, renderer=mistune.AstRenderer(),
        )
        ast = create_ast('\n'.join(lines))

        # If the length of the parsed markdown is 1, it means that the two
        # lines are part of the same block, therefore ListIndentError does not apply
        if len(ast) == 1:
            return True

        # If the type of the first element is classiefied as list
        # it is not rendered as a code block, so ListIndentError does not aplpy
        if ast[0]['type'] == 'list':  # type: ignore
            return True

        # If the seccond line is not a code block, there is no problem
        if ast[1]['type'] != 'block_code':  # type: ignore
            return True

        # If the type of the seccond line is a code block there could
        # be an error pressent, but there can be a valid code block
        # so if line starts with - it is most likely a list
        # Codeblocks can technicly start with an dash but it's very unlikely
        # to even more decrease the chance it is an actual codeblock the info property
        # is checked, info is set to the language of the code block (if given, which with most code blocks is the case)
        if ast[1]['type'] == 'block_code':  # type: ignore
            if not ast[1]['text'].startswith('-'):  # type: ignore
                return True
            if ast[1]['info']:  # type: ignore
                return True

        return False

    def fix(self, line: str) -> str:
        raise NotImplementedError


###################################
# ----- GENERAL ERROR TYPES ----- #
###################################


class ErrorMeta(TypedDict):
    """Store metadata about an error"""
    line_nr: int
    line: str
    error_type: MarkdownError


class DocumentErrors(TypedDict):
    """A helper type to keep track of errors in the documents"""
    # The filepath of the document
    file_path: str
    # List of objects {1: ErrorTyep} where the int is the line number
    errors: List[ErrorMeta]  # TODO: Change to actual types

##########################
# ----- CHECK MODE ----- #
##########################


class CheckModeArgs(TypedDict):
    """Arguments for the check mode"""
    # The input path (file or folder)
    in_path: str
    # Wheter the found mistakes should automatticly be fixed
    fix: bool


class CheckMode(BaseMode):
    """Check markdown files for errors and fix them if nessesary"""

    # The errors that can be found.
    possible_line_errors = [MathError(), TodoError()]
    possible_multi_line_errors = [SeperatorError(), ListIndentError()]

    def _check_dir(self, dir_path: str) -> List[DocumentErrors]:
        raise NotImplementedError

    def _check_file(self, file_path: str) -> DocumentErrors:
        """Opens a file and checks it for errors

        Uses the possible_errors list to check every line if a error is present

        Arguments:
            file_path {str} -- Absolute path to the file to check

        Returns:
            List[DocumentError] -- The errors that are found in the file.

        """

        errors: List[ErrorMeta] = []
        # Open file
        with open(file_path, 'r') as md_file:
            lines = md_file.readlines()
            for line_nr, line in enumerate(lines):
                # Go through the errors that can occur on the current line
                for err in self.possible_line_errors:
                    if not err.validate([line]):
                        new_err = ErrorMeta(
                            line_nr=line_nr, line=line, error_type=err,
                        )
                        errors.append(new_err)

                # Go through the errors that need multiple lines to check for errors
                for m_err in self.possible_multi_line_errors:
                    # SeperatorError needs access to multiple lines
                    if isinstance(m_err, SeperatorError):
                        if line_nr == len(lines) - 1:
                            continue
                        if not m_err.validate([line, lines[line_nr + 1]]):
                            new_err = ErrorMeta(
                                line_nr=line_nr, line=line, error_type=m_err,
                            )
                            errors.append(new_err)

                    if isinstance(m_err, ListIndentError):
                        if line_nr == len(lines) - 1:
                            continue
                        if not m_err.validate([line, lines[line_nr + 1]]):
                            new_err = ErrorMeta(
                                line_nr=line_nr, line=line, error_type=m_err,
                            )
                            errors.append(new_err)

        return DocumentErrors(file_path=file_path, errors=errors)

    def _fix_doc_errors(self, doc_errors: DocumentErrors):
        """Fixes the erros in the given document

        Arguments:
            doc_errors {DocumentErrors}  -- The document errors to fix

        Returns:
            None
        """
        # Get the file path of the current document
        file_path = doc_errors['file_path']
        wrong_line_nrs = [err['line_nr'] for err in doc_errors['errors']]
        error_types = [err['error_type'] for err in doc_errors['errors']]
        # Loop over lines
        with open(file_path, 'r') as read_file:
            lines = read_file.readlines()

        correct_lines = []
        for line_nr, line in enumerate(lines):
            # If current line is in linenumbers
            if line_nr in wrong_line_nrs:
                # Replace the current line with the correct line
                error_type = error_types[wrong_line_nrs.index(line_nr)]
                if error_type.fixable:
                    correct_line = error_type.fix(line)
                    correct_lines.append(correct_line)
                else:
                    correct_lines.append(line)
            else:
                correct_lines.append(line)

        # Write the fixed doc
        with open(file_path, 'w') as out_file:
            out_file.writelines(correct_lines)

    def _run(self, args) -> None:
        """The internal entry point for CheckMode

        Checks if the given in_path is a directory or file and
        conintues accodingly

        Arguments:
            args {CheckModeArgs} -- The arguments as parsed by the parser for the check mode

        """
        errors: List[DocumentErrors] = []
        if os.path.isdir(os.path.abspath(args['in_path'])):
            errors = self._check_dir(args['in_path'])
        elif os.path.isfile(os.path.abspath(args['in_path'])):
            doc_err = self._check_file(args['in_path'])
            if args['fix']:
                self._fix_doc_errors(doc_err)
        else:
            raise FileNotFoundError
