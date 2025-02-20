from datetime import date
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml import CommentedMap

from dapla_metadata.variable_definitions.generated.vardef_client.models.contact import (
    Contact,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.language_string_type import (
    LanguageStringType,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.owner import (
    Owner,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions.utils.time_template import get_current_time
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput


def model_to_yaml_with_comments(
    model_instance: CompletePatchOutput,
    file_path: str,
) -> str:
    """Converts a CompletePatchOutput instance to YAML with inline comments from field descriptions."""
    yaml = YAML()
    yaml.default_flow_style = False  # Ensures pretty YAML formatting
    # check this if it works
    yaml.sort_keys = False  # Prevents automatic sorting

    machine_generated_fields = [
        "id",
        "patch_id",
        "created_at",
        "created_by",
        "owner",
        "last_updated_at",
        "last_updated_by",
    ]
    data = model_instance.to_dict()  # Convert Pydantic model instance to dictionary
    machine_generated_map = CommentedMap()
    commented_map = CommentedMap()
    status_map = CommentedMap()
    # Loop through all fields in the model
    for field_name, value in data.items():
        if field_name == "variable_status":
            status_map[field_name] = value
            description = model_instance.model_fields[field_name].description
            if description:
                status_map.yaml_set_comment_before_after_key(
                    field_name,
                    before=description,
                )
        if field_name in machine_generated_fields:
            machine_generated_map[field_name] = value

            description = model_instance.model_fields[field_name].description
            if description:
                machine_generated_map.yaml_set_comment_before_after_key(
                    field_name,
                    before=description,
                )
        elif field_name != "variable_status":
            commented_map[field_name] = value
            description = model_instance.model_fields[field_name].description
            if description:
                commented_map.yaml_set_comment_before_after_key(
                    field_name,
                    before=description,
                )

    with Path.open(file_path, "w", encoding="utf-8") as file:
        commented_map.yaml_set_start_comment("--- Variable definition template ---\n")
        yaml.dump(commented_map, file)

    with Path.open(file_path, "a") as file:
        status_map.yaml_set_start_comment(
            "\n--- Status field. Value 'DRAFT' before publishing. Do not edit if creating new variable defintion ---\n",
        )
        yaml.dump(status_map, file)

    with Path.open(file_path, "a") as file:
        machine_generated_map.yaml_set_start_comment(
            "\n--- Machine generated fields. Do not edit ---\n",
        )
        yaml.dump(machine_generated_map, file)


# Have a template with default values
default_date = date(1000, 1, 1)
default_language_string_type = (
    LanguageStringType(nb="default navn", nn="default namn", en="default name"),
)

default_template = CompletePatchOutput(
    name=LanguageStringType(nb="default navn", nn="default namn", en="default name"),
    short_name="default_kortnavn",
    definition=LanguageStringType(
        nb="default definisjon",
        nn="default definisjon",
        en="default definition",
    ),
    classification_reference="code",
    valid_from=default_date,
    unit_types=["00"],
    subject_fields=["aa"],
    contains_special_categories_of_personal_data=False,
    variable_status=VariableStatus.DRAFT.value,
    owner=Owner(team="generated", groups=["generated"]),
    contact=Contact(
        title=LanguageStringType(nb="default tittel"),
        email="default@ssb.no",
    ),
    id="",
    patch_id=0,
    created_at=default_date,
    created_by="",
    last_updated_at=default_date,
    last_updated_by="",
)

model_to_yaml_with_comments(
    default_template,
    "variable_definition_template_" + get_current_time() + ".yaml",
)
