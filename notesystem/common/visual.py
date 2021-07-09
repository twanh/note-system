"""Helper functions for visual printing"""
# from notesystem.modes.search_mode import SearchMatch
# from notesystem.modes.search_mode import LineMatch
import os
from typing import Optional

from termcolor import colored

from notesystem.common.utils import clean_str
from notesystem.modes.check_mode.errors.base_errors import DocumentErrors


def print_doc_error(
    doc_errs: DocumentErrors,
    err_fixed: Optional[bool] = False,
) -> None:
    """Pretty print document errors

    Arguments:
        doc_errs {DocumentErrors} -- The document error to display
        err_fixed {bool}          -- Wether the errors are fixed (if possible)

    """
    rows, columns = os.popen('stty size', 'r').read().split()

    # Gather information to print
    file_path = doc_errs['file_path']
    file_path = clean_str(file_path)
    n_errors = len(doc_errs['errors'])

    if n_errors == 0:
        return

    max_s = int(columns) / 2
    n_dash = int(max_s - len(file_path)) - 1

    print(
        colored('-', 'cyan'), colored(
            file_path, 'cyan',
            attrs=['bold'],
        ), colored('-' * n_dash, 'cyan'),
    )
    print(
        colored(
            '* Total errors: ', 'red',
            attrs=['bold'],
        ), colored(str(n_errors), 'red'),
    )

    for i, error in enumerate(doc_errs['errors']):
        print(colored(f'  Error {i + 1}:', 'red'))
        if error['line_nr'] is not None:
            print(colored(f"    Line nr: {error['line_nr']}", 'blue'))
        else:
            print(colored('    Line nr: -', 'blue'))
        print(colored(f"    Error type: {error['error_type']}", 'blue'))
        if error['error_type'].is_fixable():
            if err_fixed:
                print(colored('    Fixed', 'blue'), colored('Yes', 'green'))
            else:
                print(
                    colored('    Auto fixable', 'blue'),
                    colored('Yes', 'green'),
                )
        else:
            if err_fixed:
                print(colored('    Fixed:', 'blue'), colored('No', 'red'))
            else:
                print(
                    colored('    Auto fixable:', 'blue'),
                    colored('No', 'red'),
                )


def print_simple_doc_error(
        doc_err: DocumentErrors,
        err_fixed: Optional[bool] = False,
):
    """Print the document errors in a simpler way

    Format:
    `notes/notes/note1.md:15 - todo-error - Fixable`
    `notes/notes/note1.md: - todo-error - Fixed`
    `notes/notes/note1.md:16 - sepperator-error - Not fixable`
    `notes/notes/note1.md:16 - sepperator-error - Not fixed`

    Arguments:
        doc_errs {DocumentErrors} -- The errors in the document
        err_fixed {bool}          -- Wether the error is fixed

    """

    file_path = clean_str(doc_err['file_path'])
    for e in doc_err['errors']:
        e_line_nr = e['line_nr'] or ''
        e_type = e['error_type'].get_error_name()

        path_print_str = colored(f'{file_path}:{e_line_nr}', 'yellow')
        type_print_str = colored(f'{e_type}', 'cyan')
        if e['error_type'].is_fixable():
            if err_fixed:
                fix_print_str = colored('Fixed', 'green')
            else:
                fix_print_str = colored('Fixable', 'green')
        else:
            if err_fixed:
                fix_print_str = colored('Not Fixed', 'red')
            else:
                fix_print_str = colored('Not fixable', 'red')

        print(f'{path_print_str} - {type_print_str} - {fix_print_str}')


def print_search_result(match, pattern: str, show_full_path: bool) -> None:
    """Pretty print search results"""

    file_path = clean_str(match['path'])
    if not show_full_path:
        file_path = file_path.split(os.sep)[-1]

    matched_lines = match['matched_lines']

    if len(matched_lines) < 1:
        return  # No matches

    for res in matched_lines:
        file_path_line_nr = colored(f'{file_path}:{res.line_nr}', 'yellow')
        line_with_pattern_highligh = res.line.replace(
            pattern,
            colored(pattern, 'grey', 'on_green'),
        ).strip()
        print(f'{file_path_line_nr}:{line_with_pattern_highligh}')
