import json
import pathlib
import shutil

import datadoc_model.all_optional.model as all_optional_model
import pytest

from dapla_metadata.datasets import Datadoc
from tests.datasets.constants import TEST_COPY_VARIABLES_FILEPATH
from tests.datasets.constants import TEST_EXISTING_METADATA_FILE_NAME


def test_copy_variable(
    metadata: Datadoc,
    tmp_path: pathlib.Path,
):
    target_short_name = "pers_id"
    shutil.copy(
        str(TEST_COPY_VARIABLES_FILEPATH), str(tmp_path / "copy_variables.json")
    )
    metadata.copy_variable(str(tmp_path / "copy_variables.json"), target_short_name)

    metadata.write_metadata_document()
    written_document = tmp_path / TEST_EXISTING_METADATA_FILE_NAME

    with pathlib.Path.open(written_document) as f:
        written_metadata = json.loads(f.read())
        datadoc_metadata = written_metadata["datadoc"]["variables"]

        assert datadoc_metadata[0]["short_name"] == target_short_name
        correct_variable = datadoc_metadata[0]
        assert correct_variable["name"] is not None
        assert correct_variable["name"][2]["languageCode"] == "nb"
        assert correct_variable["name"][2]["languageText"] == "Ny persid"


def test_variable_not_in_target_dataset(
    metadata: Datadoc,
    tmp_path: pathlib.Path,
):
    target_short_name = "test_kopiering"
    shutil.copy(
        str(TEST_COPY_VARIABLES_FILEPATH), str(tmp_path / "copy_variables.json")
    )

    with pytest.raises(
        ValueError,
        match=rf"Target variable {target_short_name} does not exist in the metadata document you are copying into!",
    ):
        metadata.copy_variable(str(tmp_path / "copy_variables.json"), target_short_name)


def test_different_source_and_target_short_name(
    metadata: Datadoc,
    tmp_path: pathlib.Path,
):
    source_short_name = "test_kopiering"
    target_short_name = "pers_id"

    shutil.copy(
        str(TEST_COPY_VARIABLES_FILEPATH), str(tmp_path / "copy_variables.json")
    )
    metadata.copy_variable(
        str(tmp_path / "copy_variables.json"), target_short_name, source_short_name
    )

    metadata.write_metadata_document()
    written_document = tmp_path / TEST_EXISTING_METADATA_FILE_NAME

    with pathlib.Path.open(written_document) as f:
        written_metadata = json.loads(f.read())
        datadoc_metadata = written_metadata["datadoc"]["variables"]

        assert datadoc_metadata[0]["short_name"] == source_short_name
        correct_variable = datadoc_metadata[0]
        assert correct_variable["name"] is not None
        assert correct_variable["name"][2]["languageCode"] == "nb"
        assert correct_variable["name"][2]["languageText"] == "Test kopiering"


def test_update_variable_error_handling(metadata: Datadoc):
    target_short_name = "non_existent"
    variable = all_optional_model.Variable(
        short_name="non_existent",
        name=[{"languageCode": "nb", "languageText": "Nytt navn"}],
        data_type=all_optional_model.DataType.STRING,
    )

    with pytest.raises(
        ValueError, match=rf"Variable with short_name '{target_short_name}' not found."
    ):
        metadata._update_variable(target_short_name, variable)  # noqa: SLF001


def test_update_variable_from_outdated_metadata_file(
    metadata: Datadoc,
    tmp_path: pathlib.Path,
):
    target_short_name = "pers_id"
    shutil.copy(
        str(TEST_COPY_VARIABLES_FILEPATH), str(tmp_path / "outdated_metadata_file.json")
    )
    metadata.copy_variable(
        str(tmp_path / "outdated_metadata_file.json"), target_short_name
    )

    metadata.write_metadata_document()
    written_document = tmp_path / TEST_EXISTING_METADATA_FILE_NAME

    with pathlib.Path.open(written_document) as f:
        written_metadata = json.loads(f.read())
        datadoc_metadata = written_metadata["datadoc"]["variables"]

        assert datadoc_metadata[0]["short_name"] == target_short_name
        correct_variable = datadoc_metadata[0]
        assert correct_variable["name"] is not None
        assert correct_variable["name"][2]["languageCode"] == "nb"
        assert correct_variable["name"][2]["languageText"] == "Ny persid"


def test_copy_multiple_variables(
    metadata: Datadoc,
    tmp_path: pathlib.Path,
):
    target_short_name = "pers_id"
    another_target_short_name = "sivilstand"
    shutil.copy(
        str(TEST_COPY_VARIABLES_FILEPATH), str(tmp_path / "copy_variables.json")
    )
    metadata.copy_variable(str(tmp_path / "copy_variables.json"), target_short_name)
    metadata.copy_variable(
        str(tmp_path / "copy_variables.json"),
        another_target_short_name,
    )

    metadata.write_metadata_document()
    written_document = tmp_path / TEST_EXISTING_METADATA_FILE_NAME

    with pathlib.Path.open(written_document) as f:
        written_metadata = json.loads(f.read())
        datadoc_metadata = written_metadata["datadoc"]["variables"]

        checks = [
            (0, target_short_name, "Ny persid"),
            (2, another_target_short_name, "Ny Sivilstand"),
        ]

        for idx, short_name, language_text in checks:
            item = datadoc_metadata[idx]
            assert item["short_name"] == short_name
            assert item["name"] is not None
            assert item["name"][2]["languageCode"] == "nb"
            assert item["name"][2]["languageText"] == language_text
