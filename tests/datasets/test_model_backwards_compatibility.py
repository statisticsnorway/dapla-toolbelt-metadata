"""Tests for the compatibility package."""

import json
from pathlib import Path

import pytest

from dapla_metadata.datasets.compatibility import is_metadata_in_container_structure
from dapla_metadata.datasets.compatibility import upgrade_metadata
from dapla_metadata.datasets.compatibility._handlers import handle_version_2_2_0
from dapla_metadata.datasets.compatibility._handlers import handle_version_3_3_0
from dapla_metadata.datasets.compatibility._handlers import handle_version_4_0_0
from dapla_metadata.datasets.compatibility._handlers import handle_version_5_0_1
from dapla_metadata.datasets.compatibility._utils import UnknownModelVersionError
from dapla_metadata.datasets.compatibility._utils import add_container
from dapla_metadata.datasets.compatibility._utils import convert_is_personal_data
from dapla_metadata.datasets.compatibility._utils import copy_pseudonymization_metadata
from dapla_metadata.datasets.core import Datadoc
from tests.datasets.constants import TEST_COMPATIBILITY_DIRECTORY
from tests.datasets.constants import TEST_EXISTING_METADATA_FILE_NAME
from tests.datasets.constants import TEST_PSEUDO_DIRECTORY

BACKWARDS_COMPATIBLE_VERSION_DIRECTORIES = [
    d for d in TEST_COMPATIBILITY_DIRECTORY.iterdir() if d.is_dir()
]

BACKWARDS_COMPATIBLE_VERSION_NAMES = [
    d.stem for d in BACKWARDS_COMPATIBLE_VERSION_DIRECTORIES
]


def test_existing_metadata_current_model_version():
    current_model_version = "6.1.0"
    fresh_metadata = {"document_version": current_model_version}
    upgraded_metadata = upgrade_metadata(fresh_metadata)
    assert upgraded_metadata == fresh_metadata


def test_handle_version_2_2_0() -> None:
    pydir: Path = Path(__file__).resolve().parent
    rootdir: Path = pydir.parent.parent
    existing_metadata_file: Path = (
        rootdir
        / TEST_COMPATIBILITY_DIRECTORY
        / "v2_2_0"
        / TEST_EXISTING_METADATA_FILE_NAME
    )
    with existing_metadata_file.open(mode="r", encoding="utf-8") as file:
        fresh_metadata = json.load(file)
    upgraded_metadata = handle_version_2_2_0(fresh_metadata)
    assert "custom_type" in upgraded_metadata["datadoc"]["dataset"]
    assert "custom_type" in upgraded_metadata["datadoc"]["variables"][0]
    assert "special_value" in upgraded_metadata["datadoc"]["variables"][0]


def test_handle_version_3_3_0() -> None:
    pydir: Path = Path(__file__).resolve().parent
    rootdir: Path = pydir.parent.parent
    existing_metadata_file: Path = (
        rootdir
        / TEST_COMPATIBILITY_DIRECTORY
        / "v3_3_0"
        / TEST_EXISTING_METADATA_FILE_NAME
    )
    with existing_metadata_file.open(mode="r", encoding="utf-8") as file:
        fresh_metadata = json.load(file)
    upgraded_metadata = handle_version_3_3_0(fresh_metadata)
    assert (
        "direct_person_identifying" not in upgraded_metadata["datadoc"]["variables"][0]
    )


def test_handle_version_4_0_0() -> None:
    pydir: Path = Path(__file__).resolve().parent
    rootdir: Path = pydir.parent.parent
    existing_metadata_file: Path = (
        rootdir
        / TEST_PSEUDO_DIRECTORY
        / "dataset_and_pseudo"
        / "v4_0_0_person_data_v1__DOC.json"
    )
    with existing_metadata_file.open(mode="r", encoding="utf-8") as file:
        fresh_metadata = json.load(file)
    upgraded_metadata = handle_version_4_0_0(fresh_metadata)
    pseudo_field = upgraded_metadata["datadoc"]["variables"][0]["pseudonymization"]
    assert pseudo_field["encryption_algorithm"] == "TINK-DAEAD"
    assert pseudo_field["encryption_key_reference"] == "ssb-common-key-1"
    assert pseudo_field["pseudonymization_time"] == "2010-09-05"
    assert pseudo_field["encryption_algorithm_parameters"] == [
        {"keyId": "ssb-common-key-1"}
    ]
    assert upgraded_metadata["datadoc"]["variables"][1]["pseudonymization"] is None


def test_handle_version_4_0_0_without_pseudo() -> None:
    pydir: Path = Path(__file__).resolve().parent
    rootdir: Path = pydir.parent.parent
    existing_metadata_file: Path = (
        rootdir
        / TEST_PSEUDO_DIRECTORY
        / "dataset_and_pseudo"
        / "no_pseudo_v4_0_0_person_data_v1__DOC.json"
    )
    with existing_metadata_file.open(mode="r", encoding="utf-8") as file:
        fresh_metadata = json.load(file)
    upgraded_metadata = handle_version_4_0_0(fresh_metadata)
    assert upgraded_metadata["datadoc"]["document_version"] == "5.0.1"


def test_handle_version_5_0_1() -> None:
    pydir: Path = Path(__file__).resolve().parent
    rootdir: Path = pydir.parent.parent
    existing_metadata_file: Path = (
        rootdir
        / TEST_COMPATIBILITY_DIRECTORY
        / "v5_0_1"
        / TEST_EXISTING_METADATA_FILE_NAME
    )
    with existing_metadata_file.open(mode="r", encoding="utf-8") as file:
        fresh_metadata = json.load(file)
    upgraded_metadata = handle_version_5_0_1(fresh_metadata)
    assert upgraded_metadata["datadoc"]["document_version"] == "6.0.0"
    removed_dataset_fields = [
        "contains_personal_data",
        "unit_type",
        "data_source",
        "temporality_type",
    ]
    for f in removed_dataset_fields:
        assert f not in upgraded_metadata["datadoc"]["dataset"]
    added_variables_fields = [
        "is_personal_data",
        "unit_type",
        "data_source",
        "temporality_type",
    ]
    for f in added_variables_fields:
        assert all(f in v for v in upgraded_metadata["datadoc"]["variables"])


def test_existing_metadata_unknown_model_version():
    fresh_metadata = {"document_version": "0.27.65"}
    with pytest.raises(UnknownModelVersionError):
        upgrade_metadata(fresh_metadata)


@pytest.mark.parametrize(
    "existing_metadata_path",
    BACKWARDS_COMPATIBLE_VERSION_DIRECTORIES,
    ids=BACKWARDS_COMPATIBLE_VERSION_NAMES,
)
def test_backwards_compatibility(
    existing_metadata_file: Path,
    metadata: Datadoc,
):
    with existing_metadata_file.open() as f:
        file_metadata = json.loads(f.read())

    if is_metadata_in_container_structure(file_metadata):
        file_metadata = file_metadata["datadoc"]

    # Just test a single value to make sure we have a working model
    assert metadata.dataset.short_name == file_metadata["dataset"]["short_name"]  # type: ignore [union-attr, index]


def test_add_container():
    doc = {
        "percentage_complete": 98,
        "document_version": "2.1.0",
        "dataset": {"short_name": "person_data_v1", "assessment": "SENSITIVE"},
    }
    doc_with_container = add_container(doc)
    assert doc_with_container["document_version"] == "0.0.1"
    assert doc_with_container["datadoc"]["document_version"] == "2.1.0"
    assert "pseudonymization" in doc_with_container


@pytest.mark.parametrize(
    ("input_value", "expected_result"),
    [
        ("NON_PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA", True),
        ("PSEUDONYMISED_ENCRYPTED_PERSONAL_DATA", True),
        ("NOT_PERSONAL_DATA", False),
        (None, None),
        (False, False),
        (True, True),
    ],
)
def test_convert_is_personal_data(input_value, expected_result):
    supplied_metadata = {"datadoc": {"variables": [{"is_personal_data": input_value}]}}

    convert_is_personal_data(supplied_metadata)

    assert (
        supplied_metadata["datadoc"]["variables"][0]["is_personal_data"]
        == expected_result
    )


def test_copy_pseudonymization_metadata_shortname_mismatch():
    supplied_metadata = {
        "datadoc": {"variables": [{"short_name": "pers_id"}]},
        "pseudonymization": {
            "document_version": "0.1.0",
            "pseudo_dataset": None,
            "pseudo_variables": [
                {
                    "short_name": "fnr",
                    "data_element_path": "fnr",
                    "data_element_pattern": "**/fnr",
                    "stable_identifier_type": None,
                    "stable_identifier_version": None,
                    "encryption_algorithm": "TINK-DAEAD",
                    "encryption_key_reference": "ssb-common-key-1",
                    "encryption_algorithm_parameters": [{"keyId": "ssb-common-key-1"}],
                    "source_variable": None,
                    "source_variable_datatype": None,
                }
            ],
        },
    }

    copy_pseudonymization_metadata(supplied_metadata)

    assert len(supplied_metadata["datadoc"]["variables"]) == 1
    assert supplied_metadata["datadoc"]["variables"][0]["pseudonymization"] is None
