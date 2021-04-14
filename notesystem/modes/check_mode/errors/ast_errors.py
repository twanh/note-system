import enum
from typing import Dict
from typing import List
from typing import Optional
from typing import TypedDict

import mistune

from notesystem.modes.check_mode.errors.base_errors import BaseError


class AstNodeTypes(enum.Enum):
    text = 'text'
    codespan = 'codepsan'
    linebreak = 'linebreak'
    inline_html = 'inline_html'
    heading = 'heading'
    newline = 'newline'
    thematic_break = 'thematic_break'
    block_code = 'block_code'
    block_html = 'block_html'
    list_block = 'list'
    list_item = 'list_item'


class AstNode(TypedDict):
    """"""
    type: AstNodeTypes
    text: Optional[str]
    children: Optional[List[Dict]]  # Actually an AST dict
    info: Optional[str]
    ordered: Optional[bool]
    level: Optional[int]
    src: Optional[str]
    alt: Optional[str]
    title: Optional[str]


class AstError(BaseError):
    """
    An error in a markdown file that can be found by checking
    the the ast of the file.
    """
    # Wether the error (type) is fixable

    fixable = False

    def _create_ast(self, lines: List[str]) -> List[AstNode]:
        # It is easier to (accuractly) detect a ListIndentError
        # using the ast and reasoning about that then using a regex
        # that matches any indented list
        create_ast = mistune.create_markdown(
            escape=False, renderer=mistune.AstRenderer(),
            # TODO: Add plugnis
        )

        ast: List[AstNode] = create_ast('\n'.join(lines))  # type: ignore

        return ast

    def validate(self, file_lines: List[str]) -> bool:
        """Validates the AST of the file

        Arguments:
            file_lines {List[str]} -- The lines that will be validated

        Returns:
            {bool} -- Wether the given lines are valid

        """

    def fix(self, file_lines: List[str]) -> List[str]:
        """Fixes the errors of it's type in the given lines"""

    def is_fixable(self) -> bool:
        return self.fixable


class ListIndentError(AstError):
    fixable = False

    def _validate_block(self, block: AstNode) -> bool:
        if block['type'] == AstNodeTypes.block_code.value:
            if block['text'] is not None:
                if block['text'].startswith('-') or block['info'] is None:
                    return False
        return True

    def validate(self, file_lines: List[str]) -> bool:
        """Check if there is a ListIndentError present in the given lines

        Arguments:
            file_lines {List[str]} -- The lines of the file to validate

        Returns:
            {bool} -- Wether the lines of the file are valid
                      (does not contain a ListIndentError)

        """
        ast = self._create_ast(file_lines)

        for block in ast:
            if not self._validate_block(block):
                return False

        return True

    def fix(self, file_lines: List[str]) -> List[str]:
        raise Exception('ListIndentError is not fixable')

    def __str__(self):
        return 'List Indent Error (list is not properly indented)'
