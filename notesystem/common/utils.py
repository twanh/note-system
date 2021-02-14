"""Commonly used utility functions"""
import os
import logging
from typing import List

def find_all_md_files(path: str) -> List[str]:
    """Finds all markdown files in the given directory

    Using os.walk all markdown files are found in the given directory.

    Arguments:
        path {str} -- The starting path (should be a directory) to search trough for the files


    Returns:
        List[str] -- The full paths of the found files

    """

    # Make sure the given path is actually a directory
    if not os.path.isdir(path):
        raise NotADirectoryError

    logger = logging.getLogger(__name__)

    # Use the absolute path so that the returned path to the file is also absolute
    abs_path = os.path.abspath(path)

    md_files: List[str] = []
    for path, _, files in os.walk(abs_path):
        for file in files:
            full_file_path = os.path.join(path, file)
            logger.debug(f"Found markdown file: {file}")
            md_files.append(full_file_path)

    return md_files
