from pathlib import Path

import pytest


@pytest.fixture
def set_temp_bucket(tmp_path: Path):
    """Fixture which set buckets."""
    buckets_dir = tmp_path / "buckets"
    buckets_dir.mkdir(parents=True, exist_ok=True)
    return buckets_dir


@pytest.fixture
def set_temp_bucket_name(set_temp_bucket):
    """Fixture which set buckets."""
    buckets_name_folder = set_temp_bucket / "bucket_name"
    buckets_name_folder.mkdir(parents=True, exist_ok=True)
    return buckets_name_folder


import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def test_directory():
    """Creates a temporary directory with test files and subdirectories."""
    temp_dir = Path(tempfile.mkdtemp())  # Create temp directory

    # Create valid and invalid files
    (
        temp_dir
        / "ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_v2.parquet"
    ).touch()
    (
        temp_dir / "stat/inndata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet"
    ).touch()
    (
        temp_dir
        / "ssb-dapla-example-data-produkt-prod/ledstill/inndata/skjema_p2018_p2020_v1"
    ).touch()
    (
        temp_dir
        / "tests/dataset/klargjorte_data/arbmark/resources/person_data_v1.parquet"
    ).touch()

    # Create a subdirectory with more files
    sub_dir = temp_dir / "subdir"
    sub_dir.mkdir()
    (
        sub_dir / "produkt/test-2/person_testdata_p2021-12-31_p2021-12-31_v1.parquet"
    ).touch()

    yield temp_dir  # Provide temp directory path to tests

    shutil.rmtree(temp_dir)  # Cleanup after tests


@pytest.fixture
def setup_test_files(tmp_path):
    """Fixture to create test files with correct names in a temp directory."""
    test_files = [
        "datadoc/utdata/person_data_p2021_v2.parquet",
        "datadoc/utdata/person_data_p2021_p2022_v2.parquet",
        "datadoc/utdata/undermappe/person_data_p2021_v2.parquet",
        "dataset/klargjorte_data/arbmark/resources/person_data_p2021-12-31_p2021-12-31_v1.parquet",
        "stat/inndata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "stat/klargjorte-data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "ledstill/inndata/skjema_p2018_p2020_v1",
        "datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.json",
    ]

    created_files = []
    for file_path in test_files:
        full_path = tmp_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.touch()
        created_files.append(full_path)

    return created_files, tmp_path


@pytest.fixture
def setup_test_files_period(tmp_path):
    """Fixture to create test files with correct names in a temp directory."""
    test_files = [
        "ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_v1.parquet",
        "dataset/klargjorte_data/arbmark/resources/person_data_v1.parquet",
    ]

    created_files = []
    for file_path in test_files:
        full_path = tmp_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.touch()
        created_files.append(full_path)

    return created_files, tmp_path


@pytest.fixture
def setup_test_files_state(tmp_path):
    """Fixture to create test files with correct names in a temp directory."""
    test_files = [
        "gs://ssb-staging-dapla-felles-data-delt/stat_reg/person_data_p2022_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/person_data_p2021_v3.parquet",
        "buckets/produkt/test-2/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ]

    created_files = []
    for file_path in test_files:
        full_path = tmp_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.touch()
        created_files.append(full_path)

    return created_files, tmp_path


@pytest.fixture
def setup_test_files_shortname(tmp_path):
    """Fixture to create test files with correct names in a temp directory."""
    test_files = [
        "gs://ssb-staging-dapla-felles-data-delt/inndata/person_data_p2022_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/klargjorte-data/person_data_p2021_v3.parquet",
        "buckets/produkt/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ]

    created_files = []
    for file_path in test_files:
        full_path = tmp_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.touch()
        created_files.append(full_path)

    return created_files, tmp_path


@pytest.fixture
def setup_test_files_ignored(tmp_path):
    """Fixture to create test files with correct names in a temp directory."""
    test_files = [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/temp/skjema_v1.parquet",
        "gs:/ssb-dapla-example-data-produkt-prod/ledstill/temp/skjema_v1.parquet",
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/inndata/temp/skjema_p2018_p2020_v2.parquet",
        "gs://ssb-dapla-example-data-produkt-prod/temp/ledstill/inndata/temp/skjema_p2018_p2020",
        "gs://ssb-dapla-example-data-produkt-prod/konfigurasjon/ledstill/inndata/skjema_p2018_p2020",
        "gs://ssb-dapla-example-data-produkt-prod/Konfigurasjon/ledstill/inndata/skjema_p2018_p2020",
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/kildedata/skjema_v1",
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/kildedata/skjema_p2018_p2020_v1",
        "gs://ssb-dapla-example-data-produkt-prod/ledstill/kildedata/skjema_p2018_p2020_v1",
    ]

    created_files = []
    for file_path in test_files:
        full_path = tmp_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.touch()
        created_files.append(full_path)

    return created_files, tmp_path


@pytest.fixture
def setup_test_files_invalid_symbols(tmp_path):
    """Fixture to create test files with correct names in a temp directory."""
    test_files = [
        "buckets/ssb-dapla-example-data-produkt-prod/ledstill/utdata/persån_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "gs://ssb-dapla-example-data-prædukt-prod/ledstill/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
    ]

    created_files = []
    for file_path in test_files:
        full_path = tmp_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.touch()
        created_files.append(full_path)

    return created_files, tmp_path


@pytest.fixture
def setup_test_files_dataset_shortname(tmp_path):
    """Fixture to create test files with correct names in a temp directory."""
    test_files = [
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/p2021_v2.parquet",
        "buckets/produkt/datadoc/brukertest/1/sykefratot/klargjorte_data/_p2021-12-31_p2021-12-31_v1.json",
    ]

    created_files = []
    for file_path in test_files:
        full_path = tmp_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.touch()
        created_files.append(full_path)

    return created_files, tmp_path
