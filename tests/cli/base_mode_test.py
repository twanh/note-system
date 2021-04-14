"""Test the default behaviour of the base mode"""
import pytest

from notesystem.modes.base_mode import BaseMode

# def test_base_mode_has_logger():
#     base_mode = BaseMode()
#     assert base_mode._logger is not None


def test_base_mode_default_behaviour():
    base_mode = BaseMode()
    with pytest.raises(NotImplementedError):
        base_mode.start({'visual': True, 'args': {}})

    assert base_mode._logger is not None
    assert base_mode._visual == True
