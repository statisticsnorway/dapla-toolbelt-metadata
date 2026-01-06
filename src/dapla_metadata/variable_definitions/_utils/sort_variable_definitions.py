"""Utilities for sorting variable definitions."""

from enum import Enum

from dapla_metadata.variable_definitions._generated.vardef_client.models.language_string_type import (
    LanguageStringType,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.owner import (
    Owner,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.supported_languages import (
    SupportedLanguages,
)
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition


class SortOption(Enum):
    NAME_ASC = "name-ascending"
    NAME_DESC = "name-descending"
    SHORT_NAME_ASC = "short_name-ascending"
    SHORT_NAME_DESC = "short_name-descending"
    OWNER_ASC = "owner-ascending"
    OWNER_DESC = "owner-descending"


# Map enum sort options to field name and set order
MAP_SORT_OPTIONS = {
    SortOption.NAME_ASC: ("name", False),
    SortOption.NAME_DESC: ("name", True),
    SortOption.SHORT_NAME_ASC: ("short_name", False),
    SortOption.SHORT_NAME_DESC: ("short_name", True),
    SortOption.OWNER_ASC: ("owner", False),
    SortOption.OWNER_DESC: ("owner", True),
}


def make_sort_key(field_name: str, sort_language: SupportedLanguages | None = None):
    """Create a robust sort key function for a given object attribute.

    The returned key function:
    - Safely handles missing or unsupported attributes
    - Performs case-insensitive sorting
    - Supports language-specific field
    - Falls back to Norwegian (NB) or empty strings when needed
    - Avoids raising exceptions during sorting
    """

    def key_func(obj: VariableDefinition):
        attr = getattr(obj, field_name, None)
        if attr is None:
            result = ""

        if isinstance(attr, LanguageStringType):
            try:
                if sort_language and hasattr(attr, sort_language):
                    val = getattr(attr, sort_language)
                    result = val.casefold() if isinstance(val, str) else ""
            except TypeError:
                val = getattr(attr, SupportedLanguages.NB, "")
                result = val.casefold() if isinstance(val, str) else ""
            result = str(attr).casefold()

        if isinstance(attr, Owner):
            result = getattr(attr, "team", "")

        if isinstance(attr, str):
            result = attr.casefold()

        return result

    return key_func
