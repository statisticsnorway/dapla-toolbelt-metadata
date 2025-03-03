"""Constants for utils."""

from datetime import date

VARIABLE_DEFINITIONS_DIR = "variable_definitions"
VARIABLE_STATUS_FIELD_NAME = "variable_status"
OWNER_FIELD_NAME = "owner"

TEMPLATE_HEADER = "--- Variable definition template ---\n"
HEADER = "--- Variable definition ---\n"

TEMPLATE_SECTION_HEADER_STATUS = "\n--- Status field. Value 'DRAFT' before publishing. Do not edit if creating new variable defintion ---\n"
TEMPLATE_SECTION_HEADER_OWNER = "\n--- Owner team and groups. Do not edit if creating new variable defintion, value is generated ---\n"
TEMPLATE_SECTION_HEADER_MACHINE_GENERATED = (
    "\n--- Machine generated fields. Do not edit ---\n"
)

DEFAULT_DATE = date(1000, 1, 1)

MACHINE_GENERATED_FIELDS = [
    "id",
    "patch_id",
    "created_at",
    "created_by",
    "last_updated_at",
    "last_updated_by",
]
