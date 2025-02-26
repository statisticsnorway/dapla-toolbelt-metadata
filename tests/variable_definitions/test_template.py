"""Test class for creating a yaml template."""

from pathlib import Path

import pytest
import ruamel.yaml

from dapla_metadata.variable_definitions.exceptions import VardefTemplateError
from dapla_metadata.variable_definitions.generated.vardef_client.models.patch import (
    Patch,
)
from dapla_metadata.variable_definitions.utils.template import _get_workspace_dir
from dapla_metadata.variable_definitions.utils.template import (
    model_to_yaml_with_comments,
)
from tests.variable_definitions.conftest import get_variable_definition_as_dict

yaml = ruamel.yaml.YAML()


def test_yaml_file_creation(work_folder_defaults: Path):
    """Test if the function generates a YAML file."""
    file_path = work_folder_defaults
    assert file_path.exists(), "YAML file was not created"


def test_yaml_content_default_values(work_folder_defaults: Path):
    """Check if the generated YAML file with default values contains the expected data."""
    with work_folder_defaults.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == "DRAFT"
    assert parsed_yaml["owner"]["team"] == "default team"


def test_yaml_content_saved_values(work_folder_saved_variable: Path) -> None:
    """Check if the generated YAML file with saved values contains the expected data."""
    with work_folder_saved_variable.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == "PUBLISHED_INTERNAL"
    assert parsed_yaml["last_updated_by"] == "ano@ssb.no"


def test_yaml_content_from_model_variable_definition(
    work_folder_variable_definition: Path,
) -> None:
    """Check if the generated YAML file with saved values contains the expected data."""
    with work_folder_variable_definition.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == "PUBLISHED_EXTERNAL"
    assert parsed_yaml["last_updated_by"] == "ano@ssb.no"


def test_yaml_content_from_model_patch(
    patch: Patch,
) -> None:
    """Check if the generated YAML file with saved values contains the expected data."""
    exception_message: str = ""
    try:
        model_to_yaml_with_comments(
            patch,
            custom_directory=None,
        )
    except VardefTemplateError as e:
        exception_message = e.message
    assert exception_message == "File not found: unknown file path"


def test_yaml_comments(work_folder_defaults: Path):
    """Ensure the YAML file includes the expected header comments."""
    with work_folder_defaults.open(encoding="utf-8") as f:
        content = f.read()

    assert "--- Variable definition template ---" in content
    assert "--- Status field" in content
    assert "--- Owner team" in content
    assert "--- Machine generated fields" in content


def test_file_name(work_folder_defaults: Path):
    """Check filename."""
    assert "variable_definition_template_" in str(work_folder_defaults)


def test_workspace_fixture(set_temp_workspace: Path, tmp_path: Path):
    workspace = set_temp_workspace
    assert workspace.exists()
    assert workspace == tmp_path / "work"


@pytest.mark.usefixtures("set_temp_workspace")
def test_get_workspace_dir_without_env_var():
    workspace_dir = _get_workspace_dir()
    assert workspace_dir.exists()
    assert workspace_dir.is_dir()


def test_generate_yaml_from_dict() -> None:
    """Check if the generated YAML file with saved values contains the expected data."""
    with pytest.raises(VardefTemplateError) as exc_info:
        model_to_yaml_with_comments(
            get_variable_definition_as_dict(),
            custom_directory=None,
        )
    assert str(exc_info.value) == "VardefTemplateError: Possible input is dict"
