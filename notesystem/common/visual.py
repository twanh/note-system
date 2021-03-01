"""Helper functions for visual printing"""
import os

from termcolor import colored

from notesystem.modes.check_mode.errors.base_errors import DocumentErrors
from notesystem.common.utils import clean_str


def print_doc_error(doc_errs: DocumentErrors, err_fixed: bool = False) -> None:
    """Perry print document errors

    Arguments:
        doc_errs {DocumentErrors} -- The document error to display
        assume_fixed {bool} -- Wether the errors are fixed (if possible)

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
            print(colored(f'    Line nr: -', 'blue'))
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
                print(colored('    Auto fixable:', 'blue'), colored('No', 'red'))
