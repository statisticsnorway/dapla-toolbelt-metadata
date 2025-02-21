"""Constants for utils."""

from datetime import date

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
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput

VARIABLE_STATUS_FIELD_NAME = "variable_status"
OWNER_FIELD_NAME = "owner"

TEMPLATE_HEADER = "--- Variable definition template ---\n"
TEMPLATE_SECTION_HEADER_STATUS = "\n--- Status field. Value 'DRAFT' before publishing. Do not edit if creating new variable defintion ---\n"
TEMPLATE_SECTION_HEADER_OWNER = "\n--- Owner team and groups. Do not edit if creating new variable defintion, value is generated ---\n"
TEMPLATE_SECTION_HEADER_MACHINE_GENERATED = (
    "\n--- Machine generated fields. Do not edit ---\n"
)

DEFAULT_DATE = date(1000, 1, 1)

DEFAULT_TEMPLATE = CompletePatchOutput(
    name=LanguageStringType(nb="default navn", nn="default namn", en="default name"),
    short_name="default_kortnavn",
    definition=LanguageStringType(
        nb="default definisjon",
        nn="default definisjon",
        en="default definition",
    ),
    classification_reference="class_id",
    valid_from=DEFAULT_DATE,
    unit_types=["00"],
    subject_fields=["aa"],
    contains_special_categories_of_personal_data=False,
    variable_status=VariableStatus.DRAFT.value,
    owner=Owner(team="default team", groups=["default group"]),
    contact=Contact(
        title=LanguageStringType(
            nb="default tittel",
            nn="default tittel",
            en="default title",
        ),
        email="default@ssb.no",
    ),
    id="",
    patch_id=0,
    created_at=DEFAULT_DATE,
    created_by="",
    last_updated_at=DEFAULT_DATE,
    last_updated_by="",
)

MACHINE_GENERATED_FIELDS = [
    "id",
    "patch_id",
    "created_at",
    "created_by",
    "last_updated_at",
    "last_updated_by",
]
