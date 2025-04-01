"""Utilities for dynamically adding extra fields to Pydantic models, specifically Norwegian descriptions."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING
from typing import cast

import ruamel.yaml
from pydantic import BaseModel
from pydantic import Field

from dapla_metadata.variable_definitions._utils.config import get_descriptions_path

if TYPE_CHECKING:
    from pydantic.config import JsonDict

logger = logging.getLogger(__name__)


def get_package_root() -> Path:
    """Get an absolute Path to the root of the package (dapla_metadata)."""
    number_of_directories_up_from_descriptions_file = 2
    return (
        Path(__file__)
        .resolve()
        .parents[number_of_directories_up_from_descriptions_file]
    )


def load_descriptions(file_path: Path) -> dict:
    """Load and return the contents of a YAML file as a dictionary.

    Args:
        file_path (Path): Path to the YAML file.

    Returns:
    dict: Parsed contents of the YAML file.
    """
    with Path.open(file_path, encoding="utf-8") as f:
        return ruamel.yaml.YAML().load(f)


def apply_norwegian_descriptions_to_model(
    model: type[BaseModel],
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

    descriptions = load_descriptions(
        get_package_root() / get_descriptions_path(),
    )

    for field_name, field_info in model.model_fields.items():
        new_description: str = descriptions.get(
            field_name,
            f"No description in norwegian found for {field_name}",
        )
        if "No description in norwegian found" in new_description:
            logger.warning("Missing description for %s", field_name)
        else:
            logger.debug("Field %s: %s", field_name, new_description)

        new_fields[field_name] = Field(  # type: ignore[call-overload]
            default=field_info.default,
            alias=field_info.alias,
            title=field_info.title,
            description=field_info.description,
            json_schema_extra=cast(
                "JsonDict",
                {
                    "norwegian_description": new_description,
                    "annotation": field_info.annotation,
                },
            ),
        )

    model.model_fields.update(new_fields)  # Apply changes
    model.model_rebuild()
