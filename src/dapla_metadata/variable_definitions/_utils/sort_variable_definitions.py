"""Utilities for sorting variable definitions."""

from enum import Enum

from dapla_metadata.datasets.utility.enums import SupportedLanguages
from dapla_metadata.variable_definitions._generated.vardef_client.models.owner import (
    Owner,
)
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition


class SortOption(Enum):
    NAME_ASC = "name-ascending"
    NAME_DESC = "name-descending"
    SHORT_NAME_ASC = "short_name-ascending"
    SHORT_NAME_DESC = "short_name-descending"
    OWNER_ASC = "owner-ascending"
    OWNER_DESC = "owner-descending"


# Map enum sort options to fieldname and set reverse order
MAP_SORT_OPTIONS = {
    SortOption.NAME_ASC: ("name", False),
    SortOption.NAME_DESC: ("name", True),
    SortOption.SHORT_NAME_ASC: ("short_name", False),
    SortOption.SHORT_NAME_DESC: ("short_name", True),
    SortOption.OWNER_ASC: ("owner", False),
    SortOption.OWNER_DESC: ("owner", True),
}


def make_sort_key(field_name: str, sort_language: SupportedLanguages | None = None):
    """Safely handle input attributes."""

    def key_func(obj: VariableDefinition):
        attr = getattr(obj, field_name, None)
        if attr is None:
            return ""
        # LanguageStringType
        if sort_language and hasattr(attr, sort_language):
            val = getattr(attr, sort_language)
            return val.casefold() if isinstance(val, str) else val

        # Owner handling
        if isinstance(attr, Owner):
            return getattr(attr, "team", "")

        if isinstance(attr, str):
            return attr.casefold()

        return attr

    return key_func
