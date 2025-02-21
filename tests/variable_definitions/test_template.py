"""Test class for creating a yaml template."""


import ruamel.yaml

from dapla_metadata.variable_definitions.utils.constants import DEFAULT_TEMPLATE
from dapla_metadata.variable_definitions.utils.template import (
    model_to_yaml_with_comments,
)
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput

yaml = ruamel.yaml.YAML()


def test_yaml_file_creation():
    """Test if the function generates a YAML file."""
    file_path = model_to_yaml_with_comments(DEFAULT_TEMPLATE)
    assert file_path.exists(), "YAML file was not created"


def test_yaml_content_default_values():
    """Check if the generated YAML file with default values contains the expected data."""
    file_path = model_to_yaml_with_comments(DEFAULT_TEMPLATE)
    with file_path.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == "DRAFT"
    assert parsed_yaml["owner"]["team"] == "default team"


def test_yaml_content_saved_values(complete_patch_output: CompletePatchOutput) -> None:
    """Check if the generated YAML file with saved values contains the expected data."""
    file_path = model_to_yaml_with_comments(complete_patch_output)
    with file_path.open(encoding="utf-8") as f:
        parsed_yaml = yaml.load(f)

    assert parsed_yaml["variable_status"] == "PUBLISHED_INTERNAL"
    assert parsed_yaml["last_updated_by"] == "ano@ssb.no"


def test_yaml_comments():
    """Ensure the YAML file includes the expected header comments."""
    file_path = model_to_yaml_with_comments(DEFAULT_TEMPLATE)

    with file_path.open(encoding="utf-8") as f:
        content = f.read()

    assert "--- Variable definition template ---" in content
    assert "--- Status field" in content
    assert "--- Owner team" in content
    assert "--- Machine generated fields" in content


def test_file_name():
    """Check filename."""
    file_path = model_to_yaml_with_comments(DEFAULT_TEMPLATE)
    assert "variable_definition_template_" in str(file_path)
