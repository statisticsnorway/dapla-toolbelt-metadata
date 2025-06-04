"""Tests for the ModelBackwardsCompatibility class."""

import json
from pathlib import Path

import pytest

from dapla_metadata.datasets.core import Datadoc
from dapla_metadata.datasets.model_backwards_compatibility import (
    UnknownModelVersionError,
)
from dapla_metadata.datasets.model_backwards_compatibility import add_container
from dapla_metadata.datasets.model_backwards_compatibility import (
    handle_container_version_0_0_1,
)
from dapla_metadata.datasets.model_backwards_compatibility import handle_version_2_2_0
from dapla_metadata.datasets.model_backwards_compatibility import handle_version_3_3_0
from dapla_metadata.datasets.model_backwards_compatibility import handle_version_4_0_0
from dapla_metadata.datasets.model_backwards_compatibility import (
    is_metadata_in_container_structure,
)
from dapla_metadata.datasets.model_backwards_compatibility import upgrade_metadata
from tests.datasets.constants import TEST_COMPATIBILITY_DIRECTORY
from tests.datasets.constants import TEST_EXISTING_METADATA_FILE_NAME
from tests.datasets.constants import TEST_PSEUDO_DIRECTORY

BACKWARDS_COMPATIBLE_VERSION_DIRECTORIES = [
    d for d in TEST_COMPATIBILITY_DIRECTORY.iterdir() if d.is_dir()
]

metadata_files = [
    json_file
    for version_dir in TEST_COMPATIBILITY_DIRECTORY.iterdir()
    if version_dir.is_dir()
    for json_file in version_dir.glob("*.json")
]
metadata_ids = [f"{file.parent.stem}::{file.name}" for file in metadata_files]


def test_existing_metadata_current_model_version():
    current_model_version = "5.0.1"
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
        / "v0_4_0_person_data_v1__DOC.json"
    )
    with existing_metadata_file.open(mode="r", encoding="utf-8") as file:
        fresh_metadata = json.load(file)
    upgraded_metadata = handle_version_4_0_0(fresh_metadata)
    pseudo_field = upgraded_metadata["datadoc"]["variables"][0]["pseudonymization"]
    assert pseudo_field["encryption_algorithm"] == "TINK-DAEAD"
    assert pseudo_field["encryption_key_reference"] == "ssb-common-key-1"
    assert pseudo_field["encryption_algorithm_parameters"] == [
        {"keyId": "ssb-common-key-1"}
    ]
    assert upgraded_metadata["datadoc"]["variables"][1]["pseudonymization"] is None


def test_handle_container_version_0_0_1() -> None:
    pydir: Path = Path(__file__).resolve().parent
    rootdir: Path = pydir.parent.parent
    existing_metadata_file: Path = (
        rootdir
        / TEST_PSEUDO_DIRECTORY
        / "dataset_and_pseudo"
        / "container_v_0_0_1_person_data_v1__DOC.json"
    )
    with existing_metadata_file.open(mode="r", encoding="utf-8") as file:
        fresh_metadata = json.load(file)
    upgraded_metadata = handle_container_version_0_0_1(fresh_metadata)
    assert "pseudonymization" not in upgraded_metadata


def test_existing_metadata_unknown_model_version():
    fresh_metadata = {"document_version": "0.27.65"}
    with pytest.raises(UnknownModelVersionError):
        upgrade_metadata(fresh_metadata)


@pytest.mark.parametrize("existing_metadata_file", metadata_files, ids=metadata_ids)
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
