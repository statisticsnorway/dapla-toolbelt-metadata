import logging
from pathlib import Path
from unittest.mock import patch

import pytest
from pytz import UnknownTimeZoneError
from yaml import YAMLError

from dapla_metadata.variable_definitions.exceptions import VardefFileError
from dapla_metadata.variable_definitions.vardef import Vardef

LOGGER = logging.getLogger(__name__)


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
        result = Vardef.write_template_to_file()
    result = str(result)
    # remove time stamp result
    result_without_timestamp = result.rsplit("_", 1)[0] + ".yaml"
    expected_result = str(
        workspace_dir / "variable_definitions/variable_definition_template.yaml",
    )
    assert result_without_timestamp == expected_result


@pytest.mark.usefixtures("set_temp_workspace")
def test_write_template_logger(tmp_path: Path, caplog):
    with patch.object(Path, "cwd", return_value=tmp_path):
        caplog.set_level(logging.INFO)
        Vardef.write_template_to_file()
        assert "Successfully written to file" in caplog.text


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
