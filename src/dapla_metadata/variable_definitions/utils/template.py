from datetime import datetime
from pathlib import Path

import pytz
from ruamel.yaml import YAML
from ruamel.yaml import CommentedMap

from dapla_metadata.variable_definitions.utils.constants import DEFAULT_TEMPLATE
from dapla_metadata.variable_definitions.utils.constants import MACHINE_GENERATED_FIELDS
from dapla_metadata.variable_definitions.utils.constants import OWNER_FIELD_NAME
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
from dapla_metadata.variable_definitions.utils.constants import (
    VARIABLE_STATUS_FIELD_NAME,
)
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput


def model_to_yaml_with_comments(
    model_instance: CompletePatchOutput = DEFAULT_TEMPLATE,
) -> Path:
    """Convert a CompletePatchOutput instance into a structured YAML template file with comments.

    This function:
    - Extracts data from a `CompletePatchOutput` instance.
    - Adds descriptive comments above each field.
    - Organizes the YAML output into logical sections with meaningful headers.
    - Saves the YAML content to a file, ensuring a predictable structure.

    The resulting file is named with a fixed filename and a timestamp to avoid overwriting previous templates.

    Args:
        model_instance (CompletePatchOutput, optional):
            The instance to convert. Defaults to `DEFAULT_TEMPLATE`.
        file_path (str, optional):
            The destination file path.

    Returns:
        str: The file path of the generated YAML file.
    """
    yaml = YAML()  # Use ruamel.yaml library
    yaml.default_flow_style = False  # Ensures pretty YAML formatting

    data = model_instance.to_dict()  # Convert Pydantic model instance to dictionary

    # One CommentMap for each section in the yaml file
    machine_generated_map = CommentedMap()
    commented_map = CommentedMap()
    status_map = CommentedMap()
    owner_map = CommentedMap()

    # Loop through all fields in the model and populate the commented maps
    for field_name, value in data.items():
        if field_name == VARIABLE_STATUS_FIELD_NAME:
            _populate_commented_map(field_name, value, status_map, model_instance)
        elif field_name == OWNER_FIELD_NAME:
            _populate_commented_map(field_name, value, owner_map, model_instance)
        elif field_name in MACHINE_GENERATED_FIELDS:
            _populate_commented_map(
                field_name,
                value,
                machine_generated_map,
                model_instance,
            )
        elif field_name not in {VARIABLE_STATUS_FIELD_NAME, OWNER_FIELD_NAME}:
            _populate_commented_map(field_name, value, commented_map, model_instance)

    # Add path/optional path
    file_path_base = Path(_file_path_base(_get_current_time()))

    # It is important to preserve the order of the yaml dump operations when writing to file
    # so that the file is predictable for the user
    with file_path_base.open("w", encoding="utf-8") as file:
        commented_map.yaml_set_start_comment(TEMPLATE_HEADER)
        yaml.dump(commented_map, file)

        status_map.yaml_set_start_comment(TEMPLATE_SECTION_HEADER_STATUS)
        yaml.dump(status_map, file)

        owner_map.yaml_set_start_comment(TEMPLATE_SECTION_HEADER_OWNER)
        yaml.dump(owner_map, file)

        machine_generated_map.yaml_set_start_comment(
            TEMPLATE_SECTION_HEADER_MACHINE_GENERATED,
        )
        yaml.dump(machine_generated_map, file)
    return file_path_base


def _populate_commented_map(
    field_name: str,
    value: str,
    commented_map: CommentedMap,
    model_instance: CompletePatchOutput,
) -> None:
    """Add data to a CommentedMap."""
    commented_map[field_name] = value
    description = model_instance.model_fields[field_name].description
    if description:
        commented_map.yaml_set_comment_before_after_key(
            field_name,
            before=description,
        )


def _file_path_base(time_object: str) -> str:
    """Return file name with dynamic timestamp."""
    return "variable_definition_template_" + time_object + ".yaml"


def _get_current_time() -> str:
    """Return a string format date now for filename."""
    timezone = pytz.timezone("Europe/Oslo")
    current_datetime = datetime.now(timezone).strftime("%Y-%m-%dT%H-%M-%S")
    return str(current_datetime)
