import os
import re
import abc
from typing import TypedDict, List, Dict, Tuple

import mistune

from notesystem.modes.base_mode import BaseMode

# Special types
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
    def validate(self, line: str) -> bool:
        """Validates the line (checks if there is an error in the line)"""

    @abc.abstractclassmethod
    def fix(self, line: str) -> str:
        """Fixes the error on the given line and returns the correct line"""


class MathError(MarkdownError):
    fixable = True
    regex_pattern = r'\$\$(.*?)\$\$'

    def validate(self, line: str) -> bool:
        """Check if there is a math error present

        Arguments:
            line {str} -- The line to check

        Returns:
            bool -- Wheter the line is valid

        """
        matches = re.search(self.regex_pattern, line)
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
    possible_errors = [MathError()]

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
            for line_nr, line in enumerate(md_file):
                for err in self.possible_errors:
                    if not err.validate(line):
                        new_err = ErrorMeta(
                            line_nr=line_nr, line=line, error_type=err,
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
