"""Shared primitives for SSB dataset names and paths."""

from __future__ import annotations

import re
from types import MappingProxyType
from typing import Final

DATASET_STATE_PATH_NAMES: Final = MappingProxyType(
    {
        "SOURCE_DATA": frozenset({"kildedata"}),
        "INPUT_DATA": frozenset({"inndata"}),
        "PROCESSED_DATA": frozenset({"klargjorte-data", "klargjorte_data"}),
        "STATISTICS": frozenset({"statistikk"}),
        "OUTPUT_DATA": frozenset({"utdata"}),
    }
)
_CANONICAL_DATA_STATE_NAME_BY_STATE: Final = MappingProxyType(
    {
        "INPUT_DATA": "inndata",
        "PROCESSED_DATA": "klargjorte-data",
        "STATISTICS": "statistikk",
        "OUTPUT_DATA": "utdata",
    }
)
CANONICAL_DATA_STATE_NAMES: Final = frozenset(
    _CANONICAL_DATA_STATE_NAME_BY_STATE.values()
)

_ILLEGAL_DATASET_SHORT_NAME_CHARS_PATTERN = re.compile(r"[^a-zA-Z0-9\-]")


def is_valid_dataset_short_name(value: str | None) -> bool:
    """Return whether a present, non-empty value only contains letters, digits, and hyphens.

    Hyphen placement is unrestricted: leading, trailing, and consecutive
    hyphens are all allowed.
    """
    if not value:
        return False
    return _ILLEGAL_DATASET_SHORT_NAME_CHARS_PATTERN.search(value) is None


def dataset_state_path_names(state_name: str) -> frozenset[str]:
    """Return accepted Norwegian path names for a dataset-state enum name."""
    return DATASET_STATE_PATH_NAMES.get(state_name, frozenset())
