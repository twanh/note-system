import abc
from typing import List
from typing import Optional
from typing import TypedDict

##########################
# ----- BASE ERROR ----- #
##########################


class BaseError(abc.ABC):
    """An error in a markdown file"""
    # Wether the error is fixable
    fixable: bool

    @abc.abstractclassmethod
    def validate(self, lines: List[str]) -> bool:
        """Validates the input lines"""

    def fix(self, inp: List[str]) -> List[str]:
        """Fixes the error given in the inp (input) and
           returns the corrected lines
        """

    def is_fixable(self) -> bool:
        """Returns wether the error is fixable"""

    # Helper functions for the command line

    @staticmethod
    def get_help_text() -> str:
        """Returns the help text to be displayed on the help menu"""

    @staticmethod
    def get_error_name() -> str:
        """Returns the name of the error to the commandline"""


############################################
# ----- GENERAL ERROR HANDLING TYPES ----- #
############################################


class ErrorMeta(TypedDict):
    """Store metadata about an error"""
    line_nr: Optional[int]
    line: Optional[str]
    error_type: BaseError


class DocumentErrors(TypedDict):
    """A helper type to keep track of errors in the documents"""
    # The filepath of the document
    file_path: str
    # List of objects {1: ErrorTyep} where the int is the line number
    errors: List[ErrorMeta]  # TODO: Change to actual types
