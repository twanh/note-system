import os
from typing import List
from typing import TypedDict

from termcolor import colored

from notesystem.common.utils import find_all_md_files
from notesystem.common.visual import print_doc_error
from notesystem.modes.base_mode import BaseMode
from notesystem.modes.check_mode.errors.ast_errors import AstError
from notesystem.modes.check_mode.errors.ast_errors import ListIndentError
from notesystem.modes.check_mode.errors.base_errors import DocumentErrors
from notesystem.modes.check_mode.errors.base_errors import ErrorMeta
from notesystem.modes.check_mode.errors.markdown_errors import MarkdownError
from notesystem.modes.check_mode.errors.markdown_errors import MathError
from notesystem.modes.check_mode.errors.markdown_errors import SeperatorError
from notesystem.modes.check_mode.errors.markdown_errors import TodoError

##########################
# ----- CHECK MODE ----- #
##########################

# ALL ERRORS

ALL_ERRORS = [MathError, TodoError, SeperatorError, ListIndentError]


class CheckModeArgs(TypedDict):
    """Arguments for the check mode"""
    # The input path (file or folder)
    in_path: str
    # Wheter the found mistakes should automatticly be fixed
    fix: bool
    # Disabled errors
    disabled_errors: List[str]


class CheckMode(BaseMode):
    """Check markdown files for errors and fix them if nessesary"""

    # The errors that can be found.
    # TODO: Replace with a more modular way
    possible_line_markdown_errors: List[MarkdownError] = [
        MathError(), TodoError(),
    ]
    possible_multi_line_markdown_errors: List[MarkdownError] = [
        SeperatorError(),
    ]

    possible_ast_errors: List[AstError] = [ListIndentError()]

    def _check_dir(self, dir_path: str) -> List[DocumentErrors]:
        """Checks all the markdown files in the given directory for errors

        Arguments:
            dir_path {str} -- The path to the directory containing the
                              markdown files to check.

        Raises:
            {NotADirectoryError} -- When the given dir_path does not exist,
                                    NotADirectoryError is raised.

        Returns:
            List[DocumentError] -- The found document errors

        """

        if not os.path.isdir(os.path.abspath(dir_path)):
            self._logger.error(
                f'Could not find directory: {os.path.abspath(dir_path)}. \
                Please provide a valid directory.',
            )
            raise NotADirectoryError

        md_files = find_all_md_files(dir_path)
        self._logger.info(f'Found {len(md_files)} to check')

        errors: List[DocumentErrors] = []
        for file in md_files:
            doc_errors = self._check_file(file)
            self._logger.info(
                f"Found {len(doc_errors['errors'])} errors in {file}",
            )
            errors.append(doc_errors)

        return errors

    def _check_file(self, file_path: str) -> DocumentErrors:
        """Opens a file and checks it for errors

        Uses the possible_errors list to check every line if a error is present

        Arguments:
            file_path {str} -- Absolute path to the file to check

        Returns:
            List[DocumentError] -- The errors that are found in the file.

        """

        # TODO: Check if file exists

        errors: List[ErrorMeta] = []
        # Open file
        lines: List[str] = []

        try:
            with open(file_path, 'r') as md_file:
                lines = md_file.readlines()
        except UnicodeDecodeError as e:
            # Try different reading mode
            # when UnicodeDecodeError error is thrown
            self._logger.debug(
                'Caught UnicodeDecodeError, swithcing read mode',
            )
            self._logger.debug(e)
            try:
                with open(file_path, 'r', encoding='windows-1252') as m_file:
                    lines = m_file.readlines()
            except Exception as e2:
                self._logger.warning(
                    f'Could not open {file_path}. Skipping the file...',
                )
                self._logger.info(e2)
                return DocumentErrors(file_path=file_path, errors=errors)
        except Exception as error:
            self._logger.warning(
                f'Could not open {file_path}. Skipping the file...',
            )
            self._logger.info(error)
            return DocumentErrors(file_path=file_path, errors=errors)

        for line_nr, line in enumerate(lines):
            # Go through the errors that can occur on the current line
            for err in self.possible_line_markdown_errors:
                if not err.validate([line]):
                    if err.get_error_name() not in self._disabled_errors:
                        new_err = ErrorMeta(
                            line_nr=line_nr, line=line, error_type=err,
                        )
                        errors.append(new_err)

            # Go through the errors that need multiple lines
            # to check for errors
            for m_err in self.possible_multi_line_markdown_errors:
                # SeperatorError needs access to multiple lines
                if isinstance(m_err, SeperatorError):
                    if line_nr == len(lines) - 1:
                        continue
                    if not m_err.validate([line, lines[line_nr + 1]]):
                        if m_err.get_error_name() not in self._disabled_errors:
                            new_err = ErrorMeta(
                                line_nr=line_nr, line=line, error_type=m_err,
                            )
                            errors.append(new_err)

        # Check ast errors
        for ast_err in self.possible_ast_errors:
            if not ast_err.validate(lines):
                if ast_err.get_error_name() not in self._disabled_errors:
                    new_err = ErrorMeta(
                        # AstErrors do not need line nummers or line values
                        # When applying the fix the whole doc will be fixed
                        line_nr=None,
                        line=None,
                        error_type=ast_err,
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
        ast_errors = [et for et in error_types if isinstance(et, AstError)]

        self._logger.info(f'Fixing {file_path}')

        # Loop over lines
        with open(file_path, 'r') as read_file:
            lines = read_file.readlines()

        correct_lines: List[str] = []
        for line_nr, line in enumerate(lines):
            # If current line is in linenumbers
            # AstErrors have no line number so these should be skipped
            if line_nr in wrong_line_nrs:
                # Replace the current line with the correct line
                error_type = error_types[wrong_line_nrs.index(line_nr)]
                if error_type.fixable:
                    fixed_lines = error_type.fix([line])
                    for fl in fixed_lines:
                        correct_lines.append(fl)
                else:
                    correct_lines.append(line)
            else:
                correct_lines.append(line)

        # Loop over all the ast errors and check if they can be fixes
        # If they can apply the fix
        # Because AstErrors.fix returns all the lines of the file
        # correct_lines can be set to the return of the fix
        for ast_err in ast_errors:
            if ast_err.fixable:
                correct_lines = ast_err.fix(lines)

        # Write the fixed doc
        with open(file_path, 'w') as out_file:
            out_file.writelines(correct_lines)

    def _run(self, args: CheckModeArgs) -> None:
        """The internal entry point for CheckMode

        Checks if the given in_path is a directory or file and
        conintues accodingly

        Arguments:
            args {CheckModeArgs} -- The arguments as parsed by the parser
                                    for the check mode

        """

        self._disabled_errors = args['disabled_errors']

        errors: List[DocumentErrors] = []
        if os.path.isdir(os.path.abspath(args['in_path'])):
            self._logger.info(f'Checking directory {args["in_path"]}')
            errors = self._check_dir(args['in_path'])
        elif os.path.isfile(os.path.abspath(args['in_path'])):
            self._logger.info(f'Checking file {args["in_path"]}')
            doc_err = self._check_file(args['in_path'])
            self._logger.info(
                f"Found {len(doc_err['errors'])} errors in {args['in_path']}",
            )
            errors.append(doc_err)
        else:
            warning_msg = (
                'Could not find file or directory: ',
                os.path.abspath(args['in_path']),
                '\nPlease provide a valid file or directory.',

            )
            if self._visual:
                print(colored(''.join(warning_msg), 'red'))
            else:
                self._logger.error(
                    *warning_msg,
                )

            raise SystemExit(1)

        if args['fix']:
            for error in errors:
                self._fix_doc_errors(error)
                if self._visual:
                    print_doc_error(error, True)
        else:
            if self._visual:
                for error in errors:
                    print_doc_error(error)
