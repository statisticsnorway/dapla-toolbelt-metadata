import contextlib
from pathlib import Path

import pytest
from datadoc_model.all_optional.model import DatadocMetadata
from datadoc_model.all_optional.model import DataType
from datadoc_model.all_optional.model import Variable

from dapla_metadata.datasets._merge import BUCKET_NAME_MESSAGE
from dapla_metadata.datasets._merge import DATA_PRODUCT_NAME_MESSAGE
from dapla_metadata.datasets._merge import DATASET_SHORT_NAME_MESSAGE
from dapla_metadata.datasets._merge import DATASET_STATE_MESSAGE
from dapla_metadata.datasets._merge import DatasetConsistencyStatus
from dapla_metadata.datasets._merge import InconsistentDatasetsError
from dapla_metadata.datasets._merge import InconsistentDatasetsWarning
from dapla_metadata.datasets._merge import check_dataset_consistency
from dapla_metadata.datasets._merge import check_ready_to_merge
from dapla_metadata.datasets._merge import check_variables_consistency
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
    )
    for r in result:
        assert r.success, f"'{r.message}' failed"


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
    )
    test_id = request.node.callspec.id
    result_entry = next(r for r in result if r.message.lower() == test_id)  # type: ignore[attr-defined]
    assert not result_entry.success


@pytest.mark.parametrize(
    ("dataset_consistency_status"),
    [
        [
            DatasetConsistencyStatus(
                message=BUCKET_NAME_MESSAGE,
                success=False,
            ),
            DatasetConsistencyStatus(
                message=DATA_PRODUCT_NAME_MESSAGE,
                success=True,
            ),
            DatasetConsistencyStatus(
                message=DATASET_STATE_MESSAGE,
                success=True,
            ),
            DatasetConsistencyStatus(
                message=DATASET_SHORT_NAME_MESSAGE,
                success=True,
            ),
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
    result = check_variables_consistency(
        metadata1.variables,
        metadata2.variables,
    )
    assert any("Variable datatypes" in r.message and not r.success for r in result)


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
        (
            VARIABLE_SHORT_NAMES,
            VARIABLE_SHORT_NAMES,
            None,
        ),
    ],
    ids=[
        "additional extracted",
        "fewer extracted",
        "renamed",
        "order changed",
        "identical",
    ],
)
def test_check_variables_consistency(
    extracted_variable_names: list[str],
    existing_variable_names: list[str],
    expected_message: str,
):
    results = check_variables_consistency(
        [Variable(short_name=name) for name in extracted_variable_names],
        [Variable(short_name=name) for name in existing_variable_names],
    )
    result = next(r for r in results if expected_message in r.message)
    assert not result.success
