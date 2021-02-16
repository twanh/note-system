import os
import re
import abc
from typing import TypedDict, List, Dict, Tuple, Union

import mistune

from notesystem.modes.base_mode import BaseMode

from notesystem.modes.check_mode.errors.base_errors import ErrorMeta, DocumentErrors
from notesystem.modes.check_mode.errors.markdown_errors import TodoError, MathError, SeperatorError

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
    possible_multi_line_errors = [SeperatorError()]

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

                    # TODO: Move to a ast error checking section
                    # if isinstance(m_err, ListIndentError):
                    #     if line_nr == 0:
                    #         continue
                    #     print(line_nr)
                    #     if not m_err.validate([line, lines[line_nr - 1]]):
                    #         new_err = ErrorMeta(
                    #             line_nr=line_nr, line=line, error_type=m_err,
                    #         )
                    #         errors.append(new_err)
                    #         print(new_err)

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
