"""Code relating to merging metadata from an existing metadata document and metadata extracted from a new dataset.

This is primarily convenience functionality for users whereby they can programmatically generate metadata without
having to manually enter it. This is primarily useful when data is sharded by time (i.e. each dataset applies for
a particular period like a month or a year). Assuming there aren't structural changes, the metadata may be reused
for all periods.

It is important to be able to detect changes in the structure of the data and warn users about this so that they can
make changes as appropriate.
"""

import copy
import logging
import warnings
from pathlib import Path
from typing import cast

import datadoc_model
import datadoc_model.all_optional.model as all_optional_model
import datadoc_model.required.model as required_model
from cloudpathlib import CloudPath

from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo
from dapla_metadata.datasets.utility.constants import (
    DATASET_FIELDS_FROM_EXISTING_METADATA,
)
from dapla_metadata.datasets.utility.constants import INCONSISTENCIES_MESSAGE
from dapla_metadata.datasets.utility.utils import OptionalDatadocMetadataType

logger = logging.getLogger(__name__)


class InconsistentDatasetsWarning(UserWarning):
    """Existing and new datasets differ significantly from one another."""


class InconsistentDatasetsError(ValueError):
    """Existing and new datasets differ significantly from one another."""


def check_dataset_consistency(
    new_dataset_path: Path | CloudPath,
    existing_dataset_path: Path,
    extracted_metadata: all_optional_model.DatadocMetadata,
    existing_metadata: OptionalDatadocMetadataType,
) -> list[dict[str, object]]:
    """Run consistency tests.

    Args:
        new_dataset_path: Path to the dataset to be documented.
        existing_dataset_path: Path stored in the existing metadata.
        extracted_metadata: Metadata extracted from a physical dataset.
        existing_metadata: Metadata from a previously created metadata document.

    Returns:
        List if dict with property name and boolean success flag
    """
    new_dataset_path_info = DaplaDatasetPathInfo(new_dataset_path)
    existing_dataset_path_info = DaplaDatasetPathInfo(existing_dataset_path)
    return [
        {
            "name": "Bucket name",
            "success": (
                new_dataset_path_info.bucket_name
                == existing_dataset_path_info.bucket_name
            ),
        },
        {
            "name": "Data product name",
            "success": (
                new_dataset_path_info.statistic_short_name
                == existing_dataset_path_info.statistic_short_name
            ),
        },
        {
            "name": "Dataset state",
            "success": (
                new_dataset_path_info.dataset_state
                == existing_dataset_path_info.dataset_state
            ),
        },
        {
            "name": "Dataset short name",
            "success": (
                new_dataset_path_info.dataset_short_name
                == existing_dataset_path_info.dataset_short_name
            ),
        },
        {
            "name": "Variable names",
            "success": (
                existing_metadata is not None
                and {v.short_name for v in extracted_metadata.variables or []}
                == {v.short_name for v in existing_metadata.variables or []}
            ),
        },
        {
            "name": "Variable datatypes",
            "success": (
                existing_metadata is not None
                and [v.data_type for v in extracted_metadata.variables or []]
                == [v.data_type for v in existing_metadata.variables or []]
            ),
        },
    ]


def check_ready_to_merge(
    results: list[dict[str, object]], *, errors_as_warnings: bool
) -> None:
    """Check if the datasets are consistent enough to make a successful merge of metadata.

    Args:
        results: List if dict with property name and boolean success flag
        errors_as_warnings: True if failing checks should be raised as warnings, not errors.

    Raises:
        InconsistentDatasetsError: If inconsistencies are found and `errors_as_warnings == False`
    """
    if failures := [result for result in results if not result["success"]]:
        msg = f"{INCONSISTENCIES_MESSAGE} {', '.join(str(f['name']) for f in failures)}"
        if errors_as_warnings:
            warnings.warn(
                message=msg,
                category=InconsistentDatasetsWarning,
                stacklevel=2,
            )
        else:
            raise InconsistentDatasetsError(
                msg,
            )


def override_dataset_fields(
    merged_metadata: all_optional_model.DatadocMetadata,
    existing_metadata: all_optional_model.DatadocMetadata
    | required_model.DatadocMetadata,
) -> None:
    """Overrides specific fields in the dataset of `merged_metadata` with values from the dataset of `existing_metadata`.

    This function iterates over a predefined list of fields, `DATASET_FIELDS_FROM_EXISTING_METADATA`,
    and sets the corresponding fields in the `merged_metadata.dataset` object to the values
    from the `existing_metadata.dataset` object.

    Args:
        merged_metadata: An instance of `DatadocMetadata` containing the dataset to be updated.
        existing_metadata: An instance of `DatadocMetadata` containing the dataset whose values are used to update `merged_metadata.dataset`.

    Returns:
        `None`.
    """
    if merged_metadata.dataset and existing_metadata.dataset:
        # Override the fields as defined
        for field in DATASET_FIELDS_FROM_EXISTING_METADATA:
            setattr(
                merged_metadata.dataset,
                field,
                getattr(existing_metadata.dataset, field),
            )


def merge_variables(
    existing_metadata: OptionalDatadocMetadataType,
    extracted_metadata: all_optional_model.DatadocMetadata,
    merged_metadata: all_optional_model.DatadocMetadata,
) -> all_optional_model.DatadocMetadata:
    """Merges variables from the extracted metadata into the existing metadata and updates the merged metadata.

    This function compares the variables from `extracted_metadata` with those in `existing_metadata`.
    For each variable in `extracted_metadata`, it checks if a variable with the same `short_name` exists
    in `existing_metadata`. If a match is found, it updates the existing variable with information from
    `extracted_metadata`. If no match is found, the variable from `extracted_metadata` is directly added to `merged_metadata`.

    Args:
        existing_metadata: The metadata object containing the current state of variables.
        extracted_metadata: The metadata object containing new or updated variables to merge.
        merged_metadata: The metadata object that will contain the result of the merge.

    Returns:
        all_optional_model.DatadocMetadata: The `merged_metadata` object containing variables from both `existing_metadata`
        and `extracted_metadata`.
    """
    if (
        existing_metadata is not None
        and existing_metadata.variables is not None
        and extracted_metadata is not None
        and extracted_metadata.variables is not None
        and merged_metadata.variables is not None
    ):
        for extracted in extracted_metadata.variables:
            existing = next(
                (
                    existing
                    for existing in existing_metadata.variables
                    if existing.short_name == extracted.short_name
                ),
                None,
            )
            if existing:
                existing.id = (
                    None  # Set to None so that it will be set assigned a fresh ID later
                )
                existing.contains_data_from = (
                    extracted.contains_data_from or existing.contains_data_from
                )
                existing.contains_data_until = (
                    extracted.contains_data_until or existing.contains_data_until
                )
                merged_metadata.variables.append(
                    cast("datadoc_model.all_optional.model.Variable", existing)
                )
            else:
                # If there is no existing metadata for this variable, we just use what we have extracted
                merged_metadata.variables.append(extracted)
    return merged_metadata


def merge_metadata(
    extracted_metadata: all_optional_model.DatadocMetadata | None,
    existing_metadata: OptionalDatadocMetadataType,
) -> all_optional_model.DatadocMetadata:
    if not existing_metadata:
        logger.warning(
            "No existing metadata found, no merge to perform. Continuing with extracted metadata.",
        )
        return extracted_metadata or all_optional_model.DatadocMetadata()

    if not extracted_metadata:
        return cast("all_optional_model.DatadocMetadata", existing_metadata)

    # Use the extracted metadata as a base
    merged_metadata = all_optional_model.DatadocMetadata(
        dataset=copy.deepcopy(extracted_metadata.dataset),
        variables=[],
    )

    override_dataset_fields(
        merged_metadata=merged_metadata,
        existing_metadata=cast("all_optional_model.DatadocMetadata", existing_metadata),
    )

    # Merge variables.
    # For each extracted variable, copy existing metadata into the merged metadata
    return merge_variables(
        existing_metadata=existing_metadata,
        extracted_metadata=extracted_metadata,
        merged_metadata=merged_metadata,
    )
