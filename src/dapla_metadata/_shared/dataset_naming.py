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
CANONICAL_DATA_STATE_NAMES: Final = frozenset(
    {
        "inndata",
        "klargjorte-data",
        "statistikk",
        "utdata",
    }
)

_DATASET_SHORT_NAME_PATTERN = re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")


def is_valid_dataset_short_name(value: str | None) -> bool:
    """Return whether a present value follows the dataset short-name syntax."""
    return (
        value is not None and _DATASET_SHORT_NAME_PATTERN.fullmatch(value) is not None
    )


def dataset_state_path_names(state_name: str) -> frozenset[str]:
    """Return accepted Norwegian path names for a dataset-state enum name."""
    return DATASET_STATE_PATH_NAMES.get(state_name, frozenset())
