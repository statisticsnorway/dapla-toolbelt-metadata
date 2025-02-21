from pathlib import Path

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
from dapla_metadata.variable_definitions.utils.time_template import get_current_time
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput


def model_to_yaml_with_comments(
    model_instance: CompletePatchOutput = DEFAULT_TEMPLATE,
    file_path: str = "",
) -> str:
    """Converts a CompletePatchOutput instance to YAML template file.

    For each field a comment above with content from field descriptions.
    """
    yaml = YAML()
    yaml.default_flow_style = False  # Ensures pretty YAML formatting
    # check this if it works
    yaml.sort_keys = False  # Prevents automatic sorting
    data = model_instance.to_dict()  # Convert Pydantic model instance to dictionary

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

    # Add path/ optional path
    file_path = _file_path_base(get_current_time())

    # It is important to preserve the order of the yaml dump operations when writing to file
    with Path.open(file_path, "w", encoding="utf-8") as file:
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


def _populate_commented_map(
    field_name: str,
    value: str,
    commented_map: CommentedMap,
    model_instance: CompletePatchOutput,
) -> CommentedMap:
    commented_map[field_name] = value
    description = model_instance.model_fields[field_name].description
    if description:
        commented_map.yaml_set_comment_before_after_key(
            field_name,
            before=description,
        )


def _file_path_base(time_object: str) -> str:
    return "variable_definition_template_" + time_object + ".yaml"
