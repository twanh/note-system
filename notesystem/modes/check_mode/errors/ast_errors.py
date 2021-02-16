from typing import List

import mistune

from notesystem.modes.check_mode.errors.base_errors import BaseError

# AST ERRORS
# ERRORS THAT CAN BE FOUND BY CHECKING THE AST OF THE WHOLE FILE


class AstError(BaseError):
    """An error in a markdown file that can be found by checking the the ast of the file"""
    # Wether the error (type) is fixable

    def validate(self, file_lines: List[str]) -> bool:
        """Validates the AST of the file (checks only for the current error type)"""

    def fix(self, file_lines: List[str]) -> List[str]:
        """Fixes the errors of it's type in the lines given and returns the fixed lines """


class ListIndentError(AstError):
    fixable = True

    def validate(self, file_lines: List[str]) -> bool:
        """Check if there is a ListIndentError present in the given lines

        Arguments:
            file {List[str]} -- The lines of the file to check

        Returns:
            {bool} -- Wether the lines of the file are valid (does not contain a ListIndentError)

        """

        # It is easier to (accuractly) detect a ListIndentError using the ast and reasoning about that
        # then using a regex that matches any indented list
        create_ast = mistune.create_markdown(
            escape=False, renderer=mistune.AstRenderer(),
        )
        # TODO: Create ast type
        ast = create_ast('\n'.join(file_lines))

        print('ast:', ast)

        # If the length of the parsed markdown is 1, it means that the two
        # lines are part of the same block, therefore ListIndentError does not apply
        if len(ast) == 1 and ast[0]['type'] != 'block_code':  # type: ignore
            return True

        # If the type of the first element is classiefied as list
        # it is not rendered as a code block, so ListIndentError does not aplpy
        if ast[0]['type'] == 'list':  # type: ignore
            return True

        if ast[0]['type'] == 'block_code':  # type: ignore
            if ast[0]['text'].startswith('-') and not ast[0]['info']:  # type: ignore
                print('CHECK 1: Error')
                return False

            # If the text does not start with blockcode and does not contain info
            # The block is invalid otherwise it is valid
            return True
            print('CHECK 1: Error')

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
        print('ERROR')
        return False

    def fix(self, file_lines: List[str]) -> List[str]:
        raise NotImplementedError
