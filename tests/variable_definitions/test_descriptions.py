"""Test class for applying norwegian descriptions to model."""

from typing import TYPE_CHECKING
from typing import cast
from unittest.mock import MagicMock
from unittest.mock import patch

from pydantic.config import JsonDict

from dapla_metadata.variable_definitions._utils.descriptions import (
    apply_norwegian_descriptions_to_model,
)
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition

if TYPE_CHECKING:
    from pydantic import JsonValue


def test_descriptions_complete_patch_output(
    get_norwegian_descriptions_from_file: dict,
):
    descriptions = get_norwegian_descriptions_from_file
    apply_norwegian_descriptions_to_model(VariableDefinition)
    field_metadata = VariableDefinition.model_fields["name"]
    field_value: JsonValue = cast(
        JsonDict,
        field_metadata.json_schema_extra,
    )["norwegian_description"]
    assert descriptions.get("name") == field_value


def test_descriptions_variable_definition(
    get_norwegian_descriptions_from_file: dict,
):
    descriptions = get_norwegian_descriptions_from_file
    apply_norwegian_descriptions_to_model(VariableDefinition)
    field_metadata = VariableDefinition.model_fields["definition"]
    field_value: JsonValue = cast(
        JsonDict,
        field_metadata.json_schema_extra,
    )["norwegian_description"]
    assert descriptions.get("definition") == field_value


@patch("dapla_metadata.variable_definitions._utils.descriptions.logger")
@patch(
    "dapla_metadata.variable_definitions._utils.descriptions.load_descriptions",
    lambda _: {},
)
def test_apply_descriptions_logs_missing_description(
    mock_logger: MagicMock,
):
    mock_field_info = MagicMock()
    mock_class = MagicMock()
    mock_class.model_fields = {"name": mock_field_info}
    mock_class = MagicMock()
    mock_class.model_fields = {"name": mock_field_info}

    apply_norwegian_descriptions_to_model(mock_class)

    # Assert that the json_schema_extra is correctly updated
    assert (
        mock_class.model_fields["name"].json_schema_extra["norwegian_description"]
        == "No description in norwegian found for name"
    )

    mock_logger.warning.assert_called_once_with(
        "Missing description for %s",
        "name",
    )
