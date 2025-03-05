import logging
from pathlib import Path
from unittest.mock import patch

import pytest
from pytz import UnknownTimeZoneError
from ruamel.yaml import YAMLError

from dapla_metadata.variable_definitions.exceptions import VardefFileError
from dapla_metadata.variable_definitions.vardef import Vardef

LOGGER = logging.getLogger(__name__)


@pytest.mark.usefixtures("set_temp_workspace")
def test_write_template():
    file_path = Vardef.write_template_to_file()
    assert file_path.exists()


def test_write_template_no_workspace(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("WORKSPACE_DIR", raising=False)
    with pytest.raises(
        VardefFileError,
        match="VardefFileError: File not found at file path: unknown file path",
    ):
        Vardef.write_template_to_file()


# monkey patch current path


def test_write_template_no_work_folder(monkeypatch: pytest.MonkeyPatch):
    """'WORKSPACE_DIR' is set but there is no path matching value."""
    monkeypatch.setenv("WORKSPACE_DIR", "statistics/a/work")

    with pytest.raises(
        VardefFileError,
        match="VardefFileError: File not found at file path: unknown file path",
    ):
        Vardef.write_template_to_file()


@pytest.mark.usefixtures("set_temp_workspace")
@pytest.mark.parametrize(
    "file_path",
    ["statistics/a/work", "./", "../..", "../", "./work"],
)
def test_write_template_workspace(tmp_path: Path, file_path):
    """Assert file is created at the correct path no mather starting point filesystem."""
    base_path = tmp_path / file_path
    base_path.mkdir(parents=True, exist_ok=True)
    # mock current directory
    with patch.object(Path, "cwd", return_value=base_path):
        file_path = Vardef.write_template_to_file()
        assert file_path.exists()


@pytest.mark.usefixtures("set_temp_workspace")
@pytest.mark.parametrize(
    "custom_path",
    ["serious", "statistics/april", "private", "toppers$#23"],
)
def test_write_template_to_custom_path_directory_doesnt_exist(
    tmp_path: Path,
    custom_path: str,
):
    file_path = Vardef.write_template_to_file(custom_file_path=tmp_path / custom_path)

    assert file_path.exists()

    file_path_str = str(file_path)

    # Not saved at default path
    assert "work" not in file_path_str
    assert "variable-definitions" not in file_path_str
    # Saved at custom path
    assert custom_path in file_path_str

    # Filename is correct
    file_name = file_path.name
    file_name_minus_timestamp = file_name.rsplit("_", 1)[0] + ".yaml"
    assert file_name_minus_timestamp == "variable_definition_template.yaml"


@pytest.mark.usefixtures("set_temp_workspace")
@pytest.mark.parametrize(
    "custom_path",
    ["problems", "statistics", "private", "toppers$#23"],
)
def test_write_template_to_custom_path_directory_exist(
    tmp_path: Path,
    custom_path: str,
):
    local_dir = tmp_path / custom_path
    local_dir.mkdir(parents=True, exist_ok=True)
    file_path = Vardef.write_template_to_file(custom_file_path=local_dir)

    assert file_path.exists()

    file_path_str = str(file_path)

    # Not saved at default path
    assert "work" not in file_path_str
    assert "variable-definitions" not in file_path_str
    # Saved at custom path
    assert custom_path in file_path_str

    # Filename is correct
    file_name = file_path.name
    file_name_minus_timestamp = file_name.rsplit("_", 1)[0] + ".yaml"
    assert file_name_minus_timestamp == "variable_definition_template.yaml"


@pytest.mark.usefixtures("_delete_workspace_dir_env_var")
def test_write_template_to_custom_path_no_workspace_dir_env(tmp_path: Path):
    file_path = Vardef.write_template_to_file(custom_file_path=tmp_path / "cki/job")
    assert file_path.exists()


# check permission error
@pytest.mark.usefixtures("set_temp_workspace")
@pytest.mark.parametrize(
    ("custom_file_path", "expected_error"),
    [
        ("my_file.yaml", ValueError),
        ("/", VardefFileError),
        ("\0", ValueError),
        ("a" * 300, OSError),
    ],
)
def test_write_template_to_invalid_custom_directory(
    custom_file_path,
    expected_error,
):
    with pytest.raises(expected_error):
        Vardef.write_template_to_file(custom_file_path=custom_file_path)


@pytest.mark.parametrize(
    ("mock_target", "side_effect"),
    [
        (
            "dapla_metadata.variable_definitions.utils.variable_definition_files._model_to_yaml_with_comments",
            FileExistsError,
        ),
        (
            "dapla_metadata.variable_definitions.utils.variable_definition_files._model_to_yaml_with_comments",
            PermissionError,
        ),
        (
            "dapla_metadata.variable_definitions.utils.variable_definition_files._get_current_time",
            UnknownTimeZoneError,
        ),
        (
            "dapla_metadata.variable_definitions.utils.variable_definition_files._model_to_yaml_with_comments",
            YAMLError,
        ),
        (
            "dapla_metadata.variable_definitions.utils.variable_definition_files._model_to_yaml_with_comments",
            EOFError,
        ),
        (
            "dapla_metadata.variable_definitions.utils.variable_definition_files._get_workspace_dir",
            NotADirectoryError,
        ),
    ],
)
def test_write_template_exceptions(mock_target: str, side_effect: Exception, mocker):
    """Test that write_template_to_file raises VardefFileError for different exceptions."""
    mocker.patch(mock_target, side_effect=side_effect)

    with pytest.raises(VardefFileError):
        Vardef.write_template_to_file()
