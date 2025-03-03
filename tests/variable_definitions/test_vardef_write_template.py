from pathlib import Path
from unittest.mock import patch

import pytest
from pytz import UnknownTimeZoneError
from yaml import YAMLError

from dapla_metadata.variable_definitions.exceptions import VardefFileError
from dapla_metadata.variable_definitions.vardef import Vardef


@pytest.mark.usefixtures("set_temp_workspace")
def test_write_template(tmp_path: Path):
    with patch.object(Path, "cwd", return_value=tmp_path):
        file_path = Vardef.write_template_to_file()
        assert file_path.exists()


@pytest.mark.usefixtures("_delete_workspace_dir")
def test_write_template_no_workspace(tmp_path: Path):
    with patch.object(Path, "cwd", return_value=tmp_path), pytest.raises(
        VardefFileError,
        match="VardefFileError: File not found at file path: unknown file path",
    ):
        Vardef.write_template_to_file()


@pytest.mark.usefixtures("_delete_workspace_dir")
def test_write_template_path_no_env_value(tmp_path: Path):
    workspace_dir = tmp_path / "work"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    with patch.object(Path, "cwd", return_value=workspace_dir):
        file_path = Vardef.write_template_to_file()
    assert file_path.exists()


def test_write_template_from_tmp_path():
    base_path = Path("../")
    with patch.object(Path, "cwd", return_value=base_path):
        file_path = Vardef.write_template_to_file()
        assert file_path.exists()


@pytest.mark.usefixtures("set_temp_workspace_invalid")
def test_write_template_invalid():
    """Env 'WORKSPACE_DIR' not present and 'work' not on path."""
    base_path = Path("../")
    base_path.mkdir(parents=True, exist_ok=True)

    with patch.object(Path, "cwd", return_value=base_path), pytest.raises(
        VardefFileError,
        match="VardefFileError: File not found at file path: unknown file path. Original error: 'work' directory not found and env WORKSPACE_DIR is not set.",
    ):
        Vardef.write_template_to_file()


@pytest.mark.usefixtures("set_env_work_dir")
def test_write_template_no_work_folder(tmp_path: Path):
    base_path = tmp_path / "statistics/a/work"
    base_path.mkdir(parents=True, exist_ok=True)

    with patch.object(Path, "cwd", return_value=base_path), pytest.raises(
        VardefFileError,
        match="VardefFileError: File not found at file path: unknown file path",
    ):
        Vardef.write_template_to_file()


@pytest.mark.usefixtures("set_temp_workspace")
def test_write_template_random_dir_work_dir(tmp_path: Path):
    base_path = tmp_path / "statistics/a/work"
    base_path.mkdir(parents=True, exist_ok=True)
    with patch.object(Path, "cwd", return_value=base_path):
        file_path = Vardef.write_template_to_file()
        assert file_path.exists()


@pytest.mark.usefixtures("set_temp_workspace")
def test_write_template_from_current():
    with patch.object(Path, "cwd", return_value=Path("./")):
        file_path = Vardef.write_template_to_file()
        assert file_path.exists()


def test_write_template_file_exists(mocker):
    mocker.patch(
        "dapla_metadata.variable_definitions.utils.variable_definition_files._model_to_yaml_with_comments",
        side_effect=FileExistsError("File already exists"),
    )

    with pytest.raises(
        VardefFileError,
        match="File already exists and can not be saved: unknown file path",
    ):
        Vardef.write_template_to_file()


def test_write_template_permission_error(mocker):
    """Test that _model_to_yaml_with_comments raises VardefFileError when a PermissionError occurs."""
    mocker.patch(
        "dapla_metadata.variable_definitions.utils.variable_definition_files._model_to_yaml_with_comments",
        side_effect=PermissionError("Permission denied"),
    )

    with pytest.raises(VardefFileError, match="Permission denied for file path"):
        Vardef.write_template_to_file()


def test_write_template_time_stamp_error(mocker):
    mocker.patch(
        "dapla_metadata.variable_definitions.utils.variable_definition_files._get_current_time",
        side_effect=UnknownTimeZoneError("Unknown timezone"),
    )

    with pytest.raises(VardefFileError, match="Timezone is unknown"):
        Vardef.write_template_to_file()


def test_yaml_serialization_error(mocker):
    """Test that write_template_to_file raises VardefFileError when yaml serialization fails."""
    mocker.patch(
        "dapla_metadata.variable_definitions.utils.variable_definition_files._model_to_yaml_with_comments",
        side_effect=YAMLError("Failed to serialize YAML"),
    )

    with pytest.raises(VardefFileError, match="Not possible to serialize yaml"):
        Vardef.write_template_to_file()


def test_write_template_to_yaml_eof_error(mocker):
    mocker.patch(
        "dapla_metadata.variable_definitions.utils.variable_definition_files._model_to_yaml_with_comments",
        side_effect=EOFError("Unexpected end of file"),
    )

    with pytest.raises(VardefFileError, match="Unexpected end of file"):
        Vardef.write_template_to_file()


def test_write_template_to_yaml_not_a_directory_error(mocker):
    workspace_dir = "variable_definitions.yaml"
    mocker.patch(
        "dapla_metadata.variable_definitions.utils.variable_definition_files._get_workspace_dir",
        side_effect=NotADirectoryError(f"'{workspace_dir}' is not a directory."),
    )

    with pytest.raises(
        VardefFileError,
        match="VardefFileError: Path is not a directory: unknown path. Original error: 'variable_definitions.yaml' is not a directory",
    ):
        Vardef.write_template_to_file()
