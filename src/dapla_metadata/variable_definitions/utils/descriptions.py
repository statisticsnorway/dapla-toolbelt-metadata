"""Utilities for dynamically adding extra fields to Pydantic models, specifically Norwegian descriptions."""
from pathlib import Path

import yaml
from pydantic import BaseModel
from pydantic import Field

from dapla_metadata.variable_definitions.utils.constants import (
    VARDEF_DESCRIPTIONS_FILE_PATH,
)


def load_descriptions(file_path: str) -> dict:
    """Load and return the contents of a YAML file as a dictionary.

    Args:
        file_path (str): Path to the YAML file.

    Returns:
    dict: Parsed contents of the YAML file.
    """
    with Path.open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


DESCRIPTIONS = load_descriptions(VARDEF_DESCRIPTIONS_FILE_PATH)


# Basemodel?
def apply_norwegian_descriptions_to_model(model: BaseModel) -> None:
    """Dynamically adds norwegian descriptions to a Pydantic model."""
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
            json_schema_extra={"norwegian_description": new_description},
        )

    model.model_fields.update(new_fields)  # Apply changes
    model.model_rebuild()
