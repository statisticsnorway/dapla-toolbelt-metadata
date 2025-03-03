"""Utilities for dynamically adding extra fields to Pydantic models, specifically Norwegian descriptions."""
import logging
from pathlib import Path
from typing import cast

import yaml
from pydantic import Field
from pydantic.config import JsonDict

from dapla_metadata.variable_definitions.config import get_descriptions_path
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition

logger = logging.getLogger(__name__)


def load_descriptions(file_path_str: str) -> dict:
    """Load and return the contents of a YAML file as a dictionary.

    Args:
        file_path_str (str): Path to the YAML file.

    Returns:
    dict: Parsed contents of the YAML file.
    """
    file_path = Path(file_path_str)
    with Path.open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


# Loads when module is imported
DESCRIPTIONS = load_descriptions(get_descriptions_path())


def apply_norwegian_descriptions_to_model(
    model: type[CompletePatchOutput] | type[VariableDefinition],
) -> None:
    """Add Norwegian descriptions to the fields of a Pydantic model.

    This function globally modifies the model fields by inserting a Norwegian description
    from a predefined dictionary. If a field does not have a corresponding
    Norwegian description, a default message is used.

    Args:
        model (BaseModel): A Pydantic model instance to be updated.

    Returns:
        None: The function modifies the model in place.
    """
    new_fields = {}

    for field_name, field_info in model.model_fields.items():
        new_description: str = DESCRIPTIONS.get(
            field_name,
            f"No description in norwegian found for {field_name}",
        )
        if "No description in norwegian found" in new_description:
            logger.warning("Missing description for %s", field_name)
        else:
            logger.info("Field %s: %s", field_name, new_description)

        new_fields[field_name] = Field(  # type: ignore[call-overload]
            default=field_info.default,
            alias=field_info.alias,
            title=field_info.title,
            description=field_info.description,
            annotation=field_info.annotation,
            json_schema_extra=cast(
                JsonDict,
                {"norwegian_description": new_description},
            ),
        )

    model.model_fields.update(new_fields)  # Apply changes
    model.model_rebuild()
