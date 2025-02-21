from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml import CommentedMap

from dapla_metadata.variable_definitions.utils.constants import DEFAULT_TEMPLATE
from dapla_metadata.variable_definitions.utils.constants import MACHINE_GENERATED_FIELDS
from dapla_metadata.variable_definitions.utils.constants import OWNER_FIELD_NAME
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
    # Loop through all fields in the model
    for field_name, value in data.items():
        if field_name == VARIABLE_STATUS_FIELD_NAME:
            _populate_commented_map(field_name, value, status_map, model_instance)
        if field_name == OWNER_FIELD_NAME:
            _populate_commented_map(field_name, value, owner_map, model_instance)
        if field_name in MACHINE_GENERATED_FIELDS:
            _populate_commented_map(
                field_name,
                value,
                machine_generated_map,
                model_instance,
            )
        elif field_name != "variable_status":
            _populate_commented_map(field_name, value, commented_map, model_instance)

    file_path = _file_path_base(get_current_time())

    with Path.open(file_path, "w", encoding="utf-8") as file:
        commented_map.yaml_set_start_comment("--- Variable definition template ---\n")
        yaml.dump(commented_map, file)

    with Path.open(file_path, "a") as file:
        status_map.yaml_set_start_comment(
            "\n--- Status field. Value 'DRAFT' before publishing. Do not edit if creating new variable defintion ---\n",
        )
        yaml.dump(status_map, file)

    with Path.open(file_path, "a") as file:
        owner_map.yaml_set_start_comment(
            "\n--- Owner team and groups. Do not edit if creating new variable defintion, value is generated ---\n",
        )
        yaml.dump(owner_map, file)

    with Path.open(file_path, "a") as file:
        machine_generated_map.yaml_set_start_comment(
            "\n--- Machine generated fields. Do not edit ---\n",
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
