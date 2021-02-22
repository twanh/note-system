import os


def test_module():
    """Run notesystem as module"""

    exit_status = os.system('python -m notesystem --help')
    assert exit_status == 0


def test_entrypoint():
    """Is it installed correctly (can be run)"""
    exit_status = os.system('notesystem --help')
    assert exit_status == 0
