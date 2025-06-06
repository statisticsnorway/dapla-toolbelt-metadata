"""Shared fixtures and configuration."""

from __future__ import annotations

import copy
import functools
import os
import pathlib
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd
import pytest
from bs4 import BeautifulSoup
from bs4 import ResultSet

from dapla_metadata.dapla.user_info import TestUserInfo
from dapla_metadata.datasets import Datadoc
from dapla_metadata.datasets.code_list import CodeList
from dapla_metadata.datasets.statistic_subject_mapping import StatisticSubjectMapping
from dapla_metadata.datasets.utility.enums import SupportedLanguages
from tests.datasets.constants import CODE_LIST_DIR
from tests.datasets.constants import DATADOC_METADATA_MODULE
from tests.datasets.constants import TEST_DATASETS_DIRECTORY
from tests.datasets.constants import TEST_EXISTING_METADATA_DIRECTORY
from tests.datasets.constants import TEST_EXISTING_METADATA_FILE_NAME
from tests.datasets.constants import TEST_EXISTING_METADATA_NAMING_STANDARD_FILEPATH
from tests.datasets.constants import TEST_NAMING_STANDARD_COMPATIBLE_DATASET
from tests.datasets.constants import TEST_PARQUET_FILE_NAME
from tests.datasets.constants import TEST_PARQUET_FILEPATH
from tests.datasets.constants import TEST_RESOURCES_DIRECTORY
from tests.datasets.test_statistic_subject_mapping import (
    STATISTICAL_SUBJECT_STRUCTURE_DIR,
)

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture(autouse=True)
def _clear_environment(mocker: MockerFixture) -> None:
    """Ensure that the environment is cleared."""
    mocker.patch.dict(os.environ, clear=True)


@pytest.fixture(scope="session", autouse=True)
def faker_session_locale():
    return ["no_NO"]


@pytest.fixture
def dummy_timestamp() -> datetime:
    return datetime(2022, 1, 1, tzinfo=timezone.utc)


@pytest.fixture
def _mock_timestamp(mocker: MockerFixture, dummy_timestamp: datetime) -> None:
    mocker.patch(
        DATADOC_METADATA_MODULE + ".core.get_timestamp_now",
        return_value=dummy_timestamp,
    )


@pytest.fixture
def _mock_user_info(mocker: MockerFixture) -> None:
    mocker.patch(
        "dapla_metadata.dapla.user_info.get_user_info_for_current_platform",
        return_value=TestUserInfo(),
    )


@pytest.fixture
def metadata(
    _mock_timestamp: None,
    _mock_user_info: None,
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    tmp_path: Path,
) -> Datadoc:
    shutil.copy(TEST_PARQUET_FILEPATH, tmp_path / TEST_PARQUET_FILE_NAME)
    return Datadoc(
        str(tmp_path / TEST_PARQUET_FILE_NAME),
        statistic_subject_mapping=subject_mapping_fake_statistical_structure,
    )


@pytest.fixture
def metadata_merged(
    _mock_timestamp: None,
    _mock_user_info: None,
    subject_mapping_fake_statistical_structure: StatisticSubjectMapping,
    tmp_path: Path,
) -> Datadoc:
    target = tmp_path / TEST_NAMING_STANDARD_COMPATIBLE_DATASET
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(
        TEST_DATASETS_DIRECTORY / TEST_NAMING_STANDARD_COMPATIBLE_DATASET,
        target,
    )
    return Datadoc(
        str(target),
        str(TEST_EXISTING_METADATA_NAMING_STANDARD_FILEPATH),
        statistic_subject_mapping=subject_mapping_fake_statistical_structure,
    )


@pytest.fixture
def existing_metadata_path() -> Path:
    return TEST_EXISTING_METADATA_DIRECTORY


@pytest.fixture
def existing_metadata_file(tmp_path: Path, existing_metadata_path: Path) -> Path:
    # Setup by copying the file into the relevant directory
    shutil.copy(
        existing_metadata_path / TEST_EXISTING_METADATA_FILE_NAME,
        tmp_path / TEST_EXISTING_METADATA_FILE_NAME,
    )
    return tmp_path / TEST_EXISTING_METADATA_FILE_NAME


@pytest.fixture
def english_name() -> str:
    return "English Name"


@pytest.fixture
def bokmål_name() -> str:  # noqa: PLC2401 the listed problems do not apply in this case
    return "Bokmål navn"


@pytest.fixture
def nynorsk_name() -> str:
    return "Nynorsk namn"


@pytest.fixture
def existing_data_path() -> Path:
    return TEST_PARQUET_FILEPATH


@pytest.fixture
def full_dataset_state_path(
    path_parts_to_insert: str | list[str],
) -> pathlib.Path:
    """Create a longer path structure from just one section.

    Examples:
    >>> full_dataset_state_path('inndata')
    'tests/dataset/inndata/resources/person_data_v1.parquet'
    >>> full_dataset_state_path(['klargjorte_data', 'arbmark'])
    'tests/dataset/klargjorte_data/arbmark/resources/person_data_v1.parquet'
    """
    split_path = list(pathlib.Path(TEST_PARQUET_FILEPATH).parts)
    new_path = copy.copy(split_path)

    if isinstance(path_parts_to_insert, str):
        parts = [path_parts_to_insert]
    else:
        parts = path_parts_to_insert
    for p in parts:
        new_path.insert(-2, p)
    return pathlib.Path().joinpath(*new_path)


@pytest.fixture
def subject_xml_file_path() -> pathlib.Path:
    return (
        TEST_RESOURCES_DIRECTORY
        / STATISTICAL_SUBJECT_STRUCTURE_DIR
        / "extract_secondary_subject.xml"
    )


@pytest.fixture
def thread_pool_executor() -> ThreadPoolExecutor:
    return ThreadPoolExecutor(max_workers=12)


@pytest.fixture
def subject_mapping_fake_statistical_structure(
    _mock_fetch_statistical_structure,
    thread_pool_executor,
) -> StatisticSubjectMapping:
    return StatisticSubjectMapping(thread_pool_executor, "placeholder")


@pytest.fixture
def _mock_fetch_statistical_structure(
    mocker,
    subject_xml_file_path: pathlib.Path,
) -> None:
    def fake_statistical_structure() -> ResultSet:
        with subject_xml_file_path.open() as f:
            return BeautifulSoup(f.read(), features="xml").find_all("hovedemne")

    mocker.patch(
        DATADOC_METADATA_MODULE
        + ".statistic_subject_mapping.StatisticSubjectMapping._fetch_data_from_external_source",
        functools.partial(fake_statistical_structure),
    )


@pytest.fixture
def subject_mapping_http_exception(
    requests_mock,
    exception_to_raise,
    thread_pool_executor,
) -> StatisticSubjectMapping:
    requests_mock.get(
        "http://test.some.url.com",
        exc=exception_to_raise,
    )
    return StatisticSubjectMapping(thread_pool_executor, "http://test.some.url.com")


@pytest.fixture
def code_list_csv_filepath_nb() -> pathlib.Path:
    return TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_nb.csv"


@pytest.fixture
def code_list_csv_filepath_nn() -> pathlib.Path:
    return TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_nn.csv"


@pytest.fixture
def code_list_csv_filepath_en() -> pathlib.Path:
    return TEST_RESOURCES_DIRECTORY / CODE_LIST_DIR / "code_list_en.csv"


@pytest.fixture
def _mock_fetch_dataframe(
    mocker,
    code_list_csv_filepath_nb: pathlib.Path,
    code_list_csv_filepath_nn: pathlib.Path,
    code_list_csv_filepath_en: pathlib.Path,
) -> None:
    def fake_code_list() -> dict[SupportedLanguages, pd.DataFrame]:
        return {
            SupportedLanguages.NORSK_BOKMÅL: pd.read_csv(
                code_list_csv_filepath_nb,
                converters={"code": str},
            ),
            SupportedLanguages.NORSK_NYNORSK: pd.read_csv(
                code_list_csv_filepath_nn,
                converters={"code": str},
            ),
            SupportedLanguages.ENGLISH: pd.read_csv(
                code_list_csv_filepath_en,
                converters={"code": str},
            ),
        }

    mocker.patch(
        DATADOC_METADATA_MODULE
        + ".code_list.CodeList._fetch_data_from_external_source",
        functools.partial(fake_code_list),
    )


@pytest.fixture
def code_list_fake_structure(_mock_fetch_dataframe, thread_pool_executor) -> CodeList:
    return CodeList(thread_pool_executor, 100)


@pytest.fixture
def copy_dataset_to_path(
    tmp_path: pathlib.Path,
    full_dataset_state_path: pathlib.Path,
) -> pathlib.Path:
    temporary_dataset = tmp_path / full_dataset_state_path
    temporary_dataset.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(TEST_PARQUET_FILEPATH, temporary_dataset)
    return temporary_dataset
