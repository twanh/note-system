import os
from typing import TypedDict, List

import mistune

from notesystem.modes.base_mode import BaseMode


class CheckModeArgs(TypedDict):
    """Arguments for the check mode"""
    # The input path (file or folder)
    in_path: str
    # Wheter the found mistakes should automatticly be fixed
    fix: bool


class DocumentError:
    """A helper type to keep track of errors in the documents"""
    file_path: str
    line_nr: int
    error_type: str  # TODO: Change to actual types


class CheckMode(BaseMode):

    def _check_dir(self, dir_path: str) -> List[DocumentError]:
        raise NotImplementedError

    def _check_file(self, file_path: str) -> List[DocumentError]:
        raise NotADirectoryError

    def _fix_errors(self, errors: List[DocumentError]):
        raise NotImplementedError

    def _run(self, args) -> None:
        """The internal entry point for CheckMode

        Checks if the given in_path is a directory or file and
        conintues accodingly

        Arguments:
            args {CheckModeArgs} -- The arguments as parsed by the parser for the check mode

        """
        errors: List[DocumentError] = []
        if os.path.isdir(os.path.abspath(args['in_path'])):
            errors = self._check_dir(args['in_path'])
        elif os.path.isfile(os.path.abspath(args['in_path'])):
            errors = self._check_file(args['in_path'])
        else:
            raise FileNotFoundError

        if args['fix']:
            self._fix_errors(errors)
