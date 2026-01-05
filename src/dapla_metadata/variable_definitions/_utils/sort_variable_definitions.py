from enum import Enum

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


FIELD_MAP = {
    SortOption.NAME_ASC: ("name", False),
    SortOption.NAME_DESC: ("name", True),
    SortOption.SHORT_NAME_ASC: ("short_name", False),
    SortOption.SHORT_NAME_DESC: ("short_name", True),
    SortOption.OWNER_ASC: ("owner", False),
    SortOption.OWNER_DESC: ("owner", True),
}


def make_key_func(field_name: str, sort_language: str | None = None):
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
