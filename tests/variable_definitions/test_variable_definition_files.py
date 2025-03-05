import logging

import pytest

from dapla_metadata.variable_definitions.exceptions import VardefFileError
from dapla_metadata.variable_definitions.utils.variable_definition_files import (
    _get_workspace_dir,
)


def test_logging_workspace_dir(caplog):
    """Test logging intended for debugging."""
    caplog.set_level(logging.DEBUG)
    _get_workspace_dir()
    assert "WORKSPACE_DIR' value:" in caplog.text


def test_workspace_dir_not_set(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("WORKSPACE_DIR", raising=False)
    with pytest.raises(
        VardefFileError,
        match="VardefFileError: WORKSPACE_DIR is not set in the configuration.",
    ):
        _get_workspace_dir()


def test_workspace_dir_doesnt_exist(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("WORKSPACE_DIR", "funnypath/haha")
    with pytest.raises(FileNotFoundError):
        _get_workspace_dir()


def test_workspace_is_not_dir(monkeypatch: pytest.MonkeyPatch, set_workspace_not_dir):
    monkeypatch.setenv("WORKSPACE_DIR", str(set_workspace_not_dir))
    with pytest.raises(NotADirectoryError):
        _get_workspace_dir()
