"""Shared primitives for SSB dataset names and paths."""

from __future__ import annotations

import re
from types import MappingProxyType
from typing import Final

_DATA_STATE_PATH_NAMES: Final = MappingProxyType(
    {
        "SOURCE_DATA": ("kildedata",),
        "INPUT_DATA": ("inndata",),
        "PROCESSED_DATA": ("klargjorte-data", "klargjorte_data"),
        "STATISTICS": ("statistikk",),
        "OUTPUT_DATA": ("utdata",),
    }
)
"""Accepted Norwegian path names per dataset-state enum name, canonical first."""

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
    return frozenset(_DATA_STATE_PATH_NAMES.get(state_name, ()))
