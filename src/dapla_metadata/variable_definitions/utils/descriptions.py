"""Utilities for dynamically adding extra fields to Pydantic models, specifically Norwegian descriptions."""
from pathlib import Path
from typing import cast

import yaml
from pydantic import Field

from dapla_metadata.variable_definitions.utils.constants import (
    VARDEF_DESCRIPTIONS_FILE_PATH,
)
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition


def load_descriptions(file_path: str) -> dict[str, str]:
    """Load and return the contents of a YAML file as a dictionary.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
    dict: Parsed contents of the YAML file.
    """
    with Path.open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# Loads when module is imported
DESCRIPTIONS = load_descriptions(VARDEF_DESCRIPTIONS_FILE_PATH)


def apply_norwegian_descriptions_to_model(
    model: type[CompletePatchOutput] | type[VariableDefinition],
) -> None:
    """Add Norwegian descriptions to the fields of a Pydantic model.

    This function updates the model fields by inserting a Norwegian description
    from a predefined dictionary (DESCRIPTIONS). If a field does not have a corresponding
    Norwegian description, a default message is used.

    Args:
        model (BaseModel): A Pydantic model instance to be updated.

    Returns:
        None: The function modifies the model in place.
    """
    new_fields = {}

    for field_name, field_info in model.model_fields.items():
        new_description = DESCRIPTIONS.get(
            field_name,
            f"No description in norwegian found for {field_name}",
        )

        new_fields[field_name] = Field(
            default=field_info.default,
            alias=field_info.alias,
            title=field_info.title,
            description=field_info.description,
            annotation=field_info.annotation,
            json_schema_extra=cast(
                dict[str, str],
                {"norwegian_description": new_description},
            ),
        )

    model.model_fields.update(new_fields)  # Apply changes
    model.model_rebuild()
