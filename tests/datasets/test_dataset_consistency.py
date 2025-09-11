import contextlib
import warnings
from pathlib import Path

import pytest
from datadoc_model.all_optional.model import DatadocMetadata
from datadoc_model.all_optional.model import DataType
from datadoc_model.all_optional.model import Variable

from dapla_metadata.datasets._merge import InconsistentDatasetsError
from dapla_metadata.datasets._merge import InconsistentDatasetsWarning
from dapla_metadata.datasets._merge import check_dataset_consistency
from dapla_metadata.datasets._merge import check_ready_to_merge
from dapla_metadata.datasets.core import Datadoc
from tests.datasets.constants import TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH
from tests.datasets.constants import VARIABLE_DATA_TYPES
from tests.datasets.constants import VARIABLE_SHORT_NAMES


@pytest.mark.parametrize(
    ("new_dataset_path", "existing_dataset_path"),
    [
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace("v1", "v2"),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace("p2021", "p2022"),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace(
                "/ifpn",
                "/deeper/folder/structure/ifpn",
            ),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
    ],
    ids=[
        "identical path",
        "differing version",
        "differing period",
        "different folder structure",
    ],
)
def test_check_dataset_consistency_consistent_paths(
    new_dataset_path: str,
    existing_dataset_path: str,
):
    result = check_dataset_consistency(
        Path(new_dataset_path),
        Path(existing_dataset_path),
        DatadocMetadata(variables=[]),
        DatadocMetadata(variables=[]),
    )
    assert all(item["success"] for item in result), "Not all 'success' is True"


@pytest.mark.parametrize(
    ("new_dataset_path", "existing_dataset_path"),
    [
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace("produkt", "delt"),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace("ifpn", "blah"),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace(
                "klargjorte_data",
                "utdata",
            ),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
        (
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH.replace(
                "person_testdata",
                "totally_different_dataset",
            ),
            TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH,
        ),
    ],
    ids=["bucket name", "data product name", "dataset state", "dataset short name"],
)
def test_check_dataset_consistency_inconsistent_paths(
    new_dataset_path: str, existing_dataset_path: str, request
):
    result = check_dataset_consistency(
        Path(new_dataset_path),
        Path(existing_dataset_path),
        DatadocMetadata(variables=[]),
        DatadocMetadata(variables=[]),
    )
    test_id = request.node.callspec.id
    result_entry = next(item for item in result if item["name"].lower() == test_id)  # type: ignore[attr-defined]
    assert not result_entry["success"]


@pytest.mark.parametrize(
    ("dataset_consistency_status"),
    [
        [
            {"name": "Bucket name", "success": False},
            {"name": "Data product name", "success": True},
            {"name": "Dataset state", "success": True},
            {"name": "Dataset short name", "success": True},
            {"name": "Variable names", "success": True},
            {"name": "Variable datatypes", "success": True},
        ],
        [
            {"name": "Bucket name", "success": True},
            {"name": "Data product name", "success": False},
            {"name": "Dataset state", "success": True},
            {"name": "Dataset short name", "success": True},
            {"name": "Variable names", "success": True},
            {"name": "Variable datatypes", "success": True},
        ],
        [
            {"name": "Bucket name", "success": True},
            {"name": "Data product name", "success": True},
            {"name": "Dataset state", "success": False},
            {"name": "Dataset short name", "success": True},
            {"name": "Variable names", "success": True},
            {"name": "Variable datatypes", "success": True},
        ],
        [
            {"name": "Bucket name", "success": True},
            {"name": "Data product name", "success": True},
            {"name": "Dataset state", "success": True},
            {"name": "Dataset short name", "success": False},
            {"name": "Variable names", "success": True},
            {"name": "Variable datatypes", "success": True},
        ],
    ],
)
@pytest.mark.parametrize(
    "errors_as_warnings",
    [True, False],
    ids=["warnings", "errors"],
)
def test_check_ready_to_merge_errors_as_warnings(
    dataset_consistency_status: list[dict[str, object]],
    errors_as_warnings: bool,
):
    with contextlib.ExitStack() as stack:
        if errors_as_warnings:
            stack.enter_context(pytest.warns(InconsistentDatasetsWarning))
        else:
            stack.enter_context(pytest.raises(InconsistentDatasetsError))
        check_ready_to_merge(
            dataset_consistency_status,
            errors_as_warnings=errors_as_warnings,
        )


expected_dataset_consistency_status = [
    {"name": "Bucket name", "success": True},
    {"name": "Data product name", "success": True},
    {"name": "Dataset state", "success": True},
    {"name": "Dataset short name", "success": True},
    {"name": "Variable names", "success": True},
    {"name": "Variable datatypes", "success": True},
]


def test_check_dataset_consistency_consistent_variables():
    variables = [
        Variable(short_name=name, data_type=data_type)
        for name, data_type in zip(
            VARIABLE_SHORT_NAMES,
            VARIABLE_DATA_TYPES,
            strict=False,
        )
    ]
    metadata = DatadocMetadata(variables=variables)
    result = check_dataset_consistency(
        Path(TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH),
        Path(TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH),
        metadata,
        metadata,
    )
    assert result == expected_dataset_consistency_status


@pytest.mark.parametrize(
    "errors_as_warnings",
    [True, False],
    ids=["warnings", "errors"],
)
def test_check_ready_to_merge_consistent_variables(
    errors_as_warnings: bool,
):
    with warnings.catch_warnings() if errors_as_warnings else contextlib.nullcontext():  # type: ignore [attr-defined]
        if errors_as_warnings:
            warnings.simplefilter("error")
        check_ready_to_merge(
            expected_dataset_consistency_status,
            errors_as_warnings=errors_as_warnings,
        )


def test_check_dataset_consistency_inconsistent_variable_data_types():
    def create_variables(data_types):
        return [
            Variable(short_name=name, data_type=data_type)
            for name, data_type in zip(VARIABLE_SHORT_NAMES, data_types, strict=False)
        ]

    metadata1 = DatadocMetadata(
        variables=create_variables(VARIABLE_DATA_TYPES[:-1] + [DataType.BOOLEAN])
    )
    metadata2 = DatadocMetadata(variables=create_variables(VARIABLE_DATA_TYPES))
    result = check_dataset_consistency(
        Path(TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH),
        Path(TEST_BUCKET_NAMING_STANDARD_COMPATIBLE_PATH),
        metadata1,
        metadata2,
    )
    assert any(
        item["name"] == "Variable datatypes" and not item["success"] for item in result
    )


@pytest.mark.parametrize(
    ("extracted_variable_names", "existing_variable_names", "expected_message"),
    [
        (
            VARIABLE_SHORT_NAMES,
            VARIABLE_SHORT_NAMES[:-2],
            "Dataset has additional variables than defined in metadata",
        ),
        (
            VARIABLE_SHORT_NAMES[:-2],
            VARIABLE_SHORT_NAMES,
            "Dataset has fewer variables than defined in metadata",
        ),
        (
            VARIABLE_SHORT_NAMES,
            [*VARIABLE_SHORT_NAMES[:-1], "blah"],
            "A variable has been renamed in the dataset",
        ),
        (
            sorted(VARIABLE_SHORT_NAMES),
            VARIABLE_SHORT_NAMES,
            "The order of variables in the dataset has changed",
        ),
    ],
    ids=["additional extracted", "fewer extracted", "renamed", "order changed"],
)
def test_check_dataset_consistency_inconsistent_variables(
    extracted_variable_names: list[str],
    existing_variable_names: list[str],
    expected_message: str,
):
    result = Datadoc._check_variables_consistency(  # noqa: SLF001
        DatadocMetadata(
            variables=[Variable(short_name=name) for name in extracted_variable_names]
        ),
        DatadocMetadata(
            variables=[Variable(short_name=name) for name in existing_variable_names]
        ),
    )
    assert any(
        item["name"] == expected_message and not item["success"] for item in result
    )
