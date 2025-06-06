from __future__ import annotations

import datetime  # import is needed in xdoctest
import logging
import pathlib
import uuid
from typing import cast

import datadoc_model
import datadoc_model.all_optional.model as all_optional_model
import datadoc_model.required.model as required_model
import google.auth
from cloudpathlib import CloudPath
from cloudpathlib import GSClient
from cloudpathlib import GSPath
from datadoc_model import model
from datadoc_model.all_optional.model import Assessment
from datadoc_model.all_optional.model import DataSetState
from datadoc_model.all_optional.model import VariableRole

from dapla_metadata.dapla import user_info
from dapla_metadata.datasets.utility.constants import (
    DATASET_FIELDS_FROM_EXISTING_METADATA,
)
from dapla_metadata.datasets.utility.constants import NUM_OBLIGATORY_VARIABLES_FIELDS
from dapla_metadata.datasets.utility.constants import (
    OBLIGATORY_DATASET_METADATA_IDENTIFIERS,
)
from dapla_metadata.datasets.utility.constants import (
    OBLIGATORY_DATASET_METADATA_IDENTIFIERS_MULTILANGUAGE,
)
from dapla_metadata.datasets.utility.constants import (
    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS,
)
from dapla_metadata.datasets.utility.constants import (
    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE,
)

logger = logging.getLogger(__name__)

DatadocMetadataType = (
    all_optional_model.DatadocMetadata | required_model.DatadocMetadata
)
DatasetType = all_optional_model.Dataset | required_model.Dataset
OptionalDatadocMetadataType = DatadocMetadataType | None


def get_timestamp_now() -> datetime.datetime:
    """Return a timestamp for the current moment."""
    return datetime.datetime.now(tz=datetime.timezone.utc)


def normalize_path(path: str) -> pathlib.Path | CloudPath:
    """Obtain a pathlib compatible Path.

    Obtains a pathlib compatible Path regardless of whether the file is on a filesystem or in GCS.

    Args:
        path: Path on a filesystem or in cloud storage.

    Returns:
        Pathlib compatible object.
    """
    if path.startswith(GSPath.cloud_prefix):
        client = GSClient(credentials=google.auth.default()[0])
        return GSPath(path, client=client)
    return pathlib.Path(path)


def calculate_percentage(completed: int, total: int) -> int:
    """Calculate percentage as a rounded integer.

    Args:
        completed: The number of completed items.
        total: The total number of items.

    Returns:
        The rounded percentage of completed items out of the total.
    """
    return round((completed / total) * 100)


def derive_assessment_from_state(state: DataSetState) -> Assessment:
    """Derive assessment from dataset state.

    Args:
        state: The state of the dataset.

    Returns:
        The derived assessment of the dataset.
    """
    match state:
        case (
            DataSetState.INPUT_DATA
            | DataSetState.PROCESSED_DATA
            | DataSetState.STATISTICS
        ):
            return Assessment.PROTECTED
        case DataSetState.OUTPUT_DATA:
            return Assessment.OPEN
        case DataSetState.SOURCE_DATA:
            return Assessment.SENSITIVE


def set_default_values_variables(variables: list) -> None:
    """Set default values on variables.

    Args:
        variables: A list of variable objects to set default values on.

    Example:
        >>> variables = [model.Variable(short_name="pers",id=None, is_personal_data = None), model.Variable(short_name="fnr",id='9662875c-c245-41de-b667-12ad2091a1ee', is_personal_data=True)]
        >>> set_default_values_variables(variables)
        >>> isinstance(variables[0].id, uuid.UUID)
        True

        >>> variables[1].is_personal_data == True
        True

        >>> variables[0].is_personal_data == False
        True
    """
    for v in variables:
        if v.id is None:
            v.id = uuid.uuid4()
        if v.is_personal_data is None:
            v.is_personal_data = False
        if v.variable_role is None:
            v.variable_role = VariableRole.MEASURE


def set_default_values_dataset(
    dataset: DatasetType,
) -> None:
    """Set default values on dataset.

    Args:
        dataset: The dataset object to set default values on.

    Example:
        >>> dataset = model.Dataset(id=None, contains_personal_data=None)
        >>> set_default_values_dataset(dataset)
        >>> dataset.id is not None
        True

        >>> dataset.contains_personal_data == False
        True
    """
    if not dataset.id:
        dataset.id = uuid.uuid4()
    if dataset.contains_personal_data is None:
        dataset.contains_personal_data = False


def set_dataset_owner(
    dataset: DatasetType,
) -> None:
    """Sets the owner of the dataset from the DAPLA_GROUP_CONTEXT enviornment variable.

    Args:
        dataset: The dataset object to set default values on.
    """
    try:
        dataset.owner = user_info.get_user_info_for_current_platform().current_team
    except OSError:
        logger.exception("Failed to find environment variable DAPLA_GROUP_CONTEXT")


def set_variables_inherit_from_dataset(
    dataset: DatasetType,
    variables: list,
) -> None:
    """Set specific dataset values on a list of variable objects.

    This function populates 'data source', 'temporality type', 'contains data from',
    and 'contains data until' fields in each variable if they are not set (None).
    The values are inherited from the corresponding fields in the dataset.

    Args:
        dataset: The dataset object from which to inherit values.
        variables: A list of variable objects to update with dataset values.

    Example:
        >>> dataset = model.Dataset(short_name='person_data_v1',data_source='01',temporality_type='STATUS',id='9662875c-c245-41de-b667-12ad2091a1ee',contains_data_from="2010-09-05",contains_data_until="2022-09-05")
        >>> variables = [model.Variable(short_name="pers",data_source =None,temporality_type = None, contains_data_from = None,contains_data_until = None)]
        >>> set_variables_inherit_from_dataset(dataset, variables)
        >>> variables[0].data_source == dataset.data_source
        True

        >>> variables[0].temporality_type is None
        False

        >>> variables[0].contains_data_from == dataset.contains_data_from
        True

        >>> variables[0].contains_data_until == dataset.contains_data_until
        True
    """
    for v in variables:
        v.contains_data_from = v.contains_data_from or dataset.contains_data_from
        v.contains_data_until = v.contains_data_until or dataset.contains_data_until
        v.temporality_type = v.temporality_type or dataset.temporality_type
        v.data_source = v.data_source or dataset.data_source


def incorrect_date_order(
    date_from: datetime.date | None,
    date_until: datetime.date | None,
) -> bool:
    """Evaluate the chronological order of two dates.

    This function checks if 'date until' is earlier than 'date from'. If so, it
    indicates an incorrect date order.

    Args:
        date_from: The start date of the time period.
        date_until: The end date of the time period.

    Returns:
        True if 'date_until' is earlier than 'date_from' or if only 'date_from' is None, False otherwise.

    Example:
        >>> incorrect_date_order(datetime.date(1980, 1, 1), datetime.date(1967, 1, 1))
        True

        >>> incorrect_date_order(datetime.date(1967, 1, 1), datetime.date(1980, 1, 1))
        False

        >>> incorrect_date_order(None, datetime.date(2024,7,1))
        True
    """
    if date_from is None and date_until is not None:
        return True
    return date_from is not None and date_until is not None and date_until < date_from


def _is_missing_multilanguage_value(
    field_name: str,
    field_value,  # noqa: ANN001 Skip type hint to enable dynamically handling value for LanguageStringType not indexable
    obligatory_list: list,
) -> bool:
    """Check obligatory fields with multilanguage value.

    This function checks whether a given field, which is supposed to have
    multilanguage values, is missing values in all specified languages.

    Args:
        field_name: The name of the field to check.
        field_value: The value of the field. Expected to be of type LanguageStringType.
        obligatory_list: A list of obligatory field names that should have multilanguage values.

    Returns:
        True if no value in any of languages for one field, False otherwise.
    """
    return bool(
        field_name in obligatory_list
        and field_value
        and (
            len(field_value[0]) > 0
            and not field_value[0]["languageText"]
            and (len(field_value) <= 1 or not field_value[1]["languageText"])
            and (len(field_value) <= 2 or not field_value[2]["languageText"])
        ),
    )


def _is_missing_metadata(
    field_name: str,
    field_value,  # noqa: ANN001 Skip type hint because method '_is_missing_multilanguage_value'
    obligatory_list: list,
    obligatory_multi_language_list: list,
) -> bool:
    """Check if an obligatory field is missing its value.

    This function checks whether a given field, which may be a simple string or a
    multilanguage value, is missing its value. It considers two lists: one for
    obligatory fields and another for obligatory multilanguage fields.

    Args:
        field_name: The name of the field to check.
        field_value: The value of the field. Can be of type str, or LanguageStringType for
            multilanguage fields.
        obligatory_list: List of obligatory fields.
        obligatory_multi_language_list: List of obligatory fields with multilanguage
            values.

    Returns:
        True if the field doesn't have a value, False otherwise.
    """
    return bool(
        (field_name in obligatory_list and field_value is None)
        or _is_missing_multilanguage_value(
            field_name,
            field_value,
            obligatory_multi_language_list,
        ),
    )


def num_obligatory_dataset_fields_completed(
    dataset: DatasetType,
) -> int:
    """Count the number of completed obligatory dataset fields.

    This function returns the total count of obligatory fields in the dataset that
    have values (are not None).

    Args:
        dataset: The dataset object for which to count the fields.

    Returns:
        The number of obligatory dataset fields that have been completed (not None).
    """
    return len(OBLIGATORY_DATASET_METADATA_IDENTIFIERS) - len(
        get_missing_obligatory_dataset_fields(dataset),
    )


def num_obligatory_variables_fields_completed(variables: list) -> int:
    """Count the number of obligatory fields completed for all variables.

    This function calculates the total number of obligatory fields that have
    values (are not None) for one variable in the list.

    Args:
        variables: A list with variable objects.

    Returns:
        The total number of obligatory variable fields that have been completed
        (not None) for all variables.
    """
    num_completed = 0
    for v in variables:
        num_completed += num_obligatory_variable_fields_completed(v)
    return num_completed


def num_obligatory_variable_fields_completed(variable: model.Variable) -> int:
    """Count the number of obligatory fields completed for one variable.

    This function calculates the total number of obligatory fields that have
    values (are not None) for one variable in the list.

    Args:
        variable: The variable to count obligatory fields for.

    Returns:
        The total number of obligatory variable fields that have been completed
        (not None) for one variable.
    """
    missing_metadata = [
        key
        for key, value in variable.model_dump().items()
        if _is_missing_metadata(
            key,
            value,
            OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS,
            OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE,
        )
    ]
    return NUM_OBLIGATORY_VARIABLES_FIELDS - len(missing_metadata)


def get_missing_obligatory_dataset_fields(
    dataset: DatasetType,
) -> list:
    """Identify all obligatory dataset fields that are missing values.

    This function checks for obligatory fields that are either directly missing
    (i.e., set to `None`) or have multilanguage values with empty content.

    Args:
        dataset: The dataset object to examine. This object must support the
            `model_dump()` method which returns a dictionary of field names and
            values.

    Returns:
        A list of field names (as strings) that are missing values. This includes:
            - Fields that are directly `None` and are listed as obligatory metadata.
            - Multilanguage fields (listed as obligatory metadata`) where
            the value exists but the primary language text is empty.
    """
    return [
        key
        for key, value in dataset.model_dump().items()
        if _is_missing_metadata(
            key,
            value,
            OBLIGATORY_DATASET_METADATA_IDENTIFIERS,
            OBLIGATORY_DATASET_METADATA_IDENTIFIERS_MULTILANGUAGE,
        )
    ]


def get_missing_obligatory_variables_fields(variables: list) -> list[dict]:
    """Identify obligatory variable fields that are missing values for each variable.

    This function checks for obligatory fields that are either directly missing
    (i.e., set to `None`) or have multilanguage values with empty content.

    Args:
        variables: A list of variable objects to check for missing obligatory fields.

    Returns:
        A list of dictionaries with variable short names as keys and list of missing
        obligatory variable fields as values. This includes:
            - Fields that are directly `None` and are llisted as obligatory metadata.
            - Multilanguage fields (listed as obligatory metadata) where the value
            exists but the primary language text is empty.
    """
    missing_variables_fields = [
        {
            variable.short_name: [
                key
                for key, value in variable.model_dump().items()
                if _is_missing_metadata(
                    key,
                    value,
                    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS,
                    OBLIGATORY_VARIABLES_METADATA_IDENTIFIERS_MULTILANGUAGE,
                )
            ],
        }
        for variable in variables
    ]
    # Filtering out variable keys with empty values list
    return [item for item in missing_variables_fields if next(iter(item.values()))]


def running_in_notebook() -> bool:
    """Return True if running in Jupyter Notebook."""
    try:
        return bool(get_ipython().__class__.__name__ == "ZMQInteractiveShell")  # type: ignore [name-defined]
    except NameError:
        # The get_ipython method is globally available in ipython interpreters
        # as used in Jupyter. However it is not available in other python
        # interpreters and will throw a NameError. Therefore we're not running
        # in Jupyter.
        return False


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
