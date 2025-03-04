"""Test class for creating a yaml template."""

from pathlib import Path

import pytest
import ruamel.yaml

from dapla_metadata.variable_definitions.utils.constants import TEMPLATE_HEADER
from dapla_metadata.variable_definitions.utils.constants import (
    TEMPLATE_SECTION_HEADER_MACHINE_GENERATED,
)
from dapla_metadata.variable_definitions.utils.constants import (
    TEMPLATE_SECTION_HEADER_OWNER,
)
from dapla_metadata.variable_definitions.utils.constants import (
    TEMPLATE_SECTION_HEADER_STATUS,
)
from dapla_metadata.variable_definitions.utils.variable_definition_files import (
    _get_workspace_dir,
)
from dapla_metadata.variable_definitions.utils.variable_definition_files import (
    create_template_yaml,
)
from tests.variable_definitions.conftest import VARIABLE_DEFINITION_DICT

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


def test_yaml_content_saved_values(work_folder_variable_definition: Path) -> None:
    """Check if the generated YAML file with saved values contains the expected data."""
    with work_folder_variable_definition.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == "PUBLISHED_EXTERNAL"
    assert parsed_yaml["last_updated_by"] == "ano@ssb.no"


def test_yaml_content_from_model_variable_definition(
    work_folder_variable_definition: Path,
) -> None:
    """Check if the generated YAML file with saved values contains the expected data."""
    with work_folder_variable_definition.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == "PUBLISHED_EXTERNAL"
    assert parsed_yaml["last_updated_by"] == "ano@ssb.no"


def test_yaml_comments(work_folder_defaults: Path):
    """Ensure the YAML file includes the expected header comments."""
    with work_folder_defaults.open(encoding="utf-8") as f:
        content = f.read()

    assert TEMPLATE_HEADER in content
    assert TEMPLATE_SECTION_HEADER_STATUS.strip() in content.strip()
    assert TEMPLATE_SECTION_HEADER_OWNER.strip() in content.strip()
    assert TEMPLATE_SECTION_HEADER_MACHINE_GENERATED.strip() in content.strip()


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
    with pytest.raises(AttributeError) as exc_info:
        create_template_yaml(
            VARIABLE_DEFINITION_DICT,  # type: ignore[arg-type]
            custom_directory=None,
        )
    assert str(exc_info.value) == "'dict' object has no attribute 'model_dump'"
