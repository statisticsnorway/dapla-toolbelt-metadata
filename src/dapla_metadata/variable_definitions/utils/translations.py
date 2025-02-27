from pathlib import Path

import yaml
from pydantic import Field

from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput


def load_translations(file_path: str) -> dict:
    """Read content of yaml file."""
    with Path.open(file_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


TRANSLATIONS = load_translations(
    "src/dapla_metadata/variable_definitions/utils/variable_definition_fields_descriptions.yaml",
)


# Basemodel?
def apply_translations_to_model(model: CompletePatchOutput) -> None:
    """Dynamically adds translated descriptions to a Pydantic model."""
    new_fields = {}

    for field_name, field_info in model.model_fields.items():
        translated_description = TRANSLATIONS.get(
            field_name,
            f"Translated {field_name}",
        )

        new_fields[field_name] = Field(
            default=field_info.default,
            alias=field_info.alias,
            title=field_info.title,
            description=field_info.description,
            annotation=field_info.annotation,
            json_schema_extra={"translated_description": translated_description},
        )

    model.model_fields.update(new_fields)  # Apply changes
    model.model_rebuild()
