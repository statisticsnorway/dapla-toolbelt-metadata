"""Test class for applying norwegian descriptions to model."""

from typing import cast

from pydantic.config import JsonDict

from dapla_metadata.variable_definitions.utils.descriptions import (
    apply_norwegian_descriptions_to_model,
)
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition


def test_descriptions_complete_patch_output(
    get_norwegian_descriptions_from_file: dict,
):
    descriptions = get_norwegian_descriptions_from_file
    apply_norwegian_descriptions_to_model(CompletePatchOutput)
    field_metadata = CompletePatchOutput.model_fields["name"]
    field_value: JsonDict = cast(
        JsonDict,
        field_metadata.json_schema_extra["norwegian_description"],
    )  # type: ignore[index]
    assert descriptions.get("name") == field_value


def test_descriptions_variable_definition(
    get_norwegian_descriptions_from_file: dict,
):
    descriptions = get_norwegian_descriptions_from_file
    apply_norwegian_descriptions_to_model(VariableDefinition)
    field_metadata = VariableDefinition.model_fields["definition"]
    field_value: JsonDict = cast(
        JsonDict,
        field_metadata.json_schema_extra["norwegian_description"],
    )  # type: ignore[index]
    assert descriptions.get("definition") == field_value
