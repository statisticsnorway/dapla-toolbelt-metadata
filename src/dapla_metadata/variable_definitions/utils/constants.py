"""Constants for variable definitions."""

from datetime import date

VARIABLE_DEFINITIONS_DIR = "variable_definitions"

VARIABLE_STATUS_FIELD_NAME = "variable_status"
OWNER_FIELD_NAME = "owner"

TEMPLATE_HEADER = "--- Variabeldefinisjon mal ---\n"
HEADER = "--- Variabeldefinisjon ---\n"

TEMPLATE_SECTION_HEADER_STATUS = "\n--- Statusfelt. Verdi 'DRAFT' før publisering. Ikke rediger hvis du oppretter en ny variabeldefinisjon. ---\n"
TEMPLATE_SECTION_HEADER_OWNER = "\n--- Eierteam og grupper. Ikke rediger hvis du oppretter en ny variabeldefinisjon, verdien genereres ---\n"
TEMPLATE_SECTION_HEADER_MACHINE_GENERATED = (
    "\n--- Maskin-genererte felt. Ikke rediger. ---\n"
)

TEMPLATE_HEADER_EN = "--- Variable definition template ---\n"
HEADER_EN = "--- Variable definition ---\n"
TEMPLATE_SECTION_HEADER_STATUS_EN = "\n--- Status field. Value 'DRAFT' before publishing. Do not edit if creating new variable defintion ---\n"
TEMPLATE_SECTION_HEADER_OWNER_EN = "\n--- Owner team and groups. Do not edit if creating new variable defintion, value is generated ---\n"
TEMPLATE_SECTION_HEADER_MACHINE_GENERATED_EN = (
    "\n--- Machine generated fields. Do not edit ---\n"
)

NORWEGIAN_DESCRIPTIONS = "norwegian_description"

DEFAULT_DATE = date(1000, 1, 1)

MACHINE_GENERATED_FIELDS = [
    "id",
    "patch_id",
    "created_at",
    "created_by",
    "last_updated_at",
    "last_updated_by",
]

OPTIONAL_FIELD = "~ Valgfritt felt ~"
REQUIRED_FIELD = "! Obligatorisk felt !"
