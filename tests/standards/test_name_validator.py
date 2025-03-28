from pathlib import Path

import pytest

from dapla_metadata.standards.name_validator import NameStandardValidator
from dapla_metadata.standards.utils.constants import MISSING_DATASET_SHORT_NAME
from dapla_metadata.standards.utils.constants import MISSING_PERIOD
from dapla_metadata.standards.utils.constants import NAME_STANDARD_SUCSESS


@pytest.mark.parametrize(
    ("file_path"),
    [
        "buckets/produkt/datadoc/utdata/person_data_p2021_v2.parquet",
        "produkt/datadoc/utdata/person_data_p2021_p2022_v2.parquet",
        "datadoc/utdata/undermappe/person_data_p2021_v2.parquet",
        "delt-data/dataset/klargjorte_data/arbmark/resources/person_data_p2021-12-31_p2021-12-31_v1.parquet",
        "stat/inndata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "ssb-delt/stat/klargjorte-data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "ssb-test/ledstill/inndata/skjema_p2018_p2020_v1",
        "produkt-delt/datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "samfunns-produkt/datadoc/brukertest/1/sykefratot/klargjorte_data/person_testdata_p2021-12-31_p2021-12-31_v1.json",
    ],
)
def test_validate_sucsess(file_path, tmp_path):
    full_path = tmp_path / file_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.touch()
    path_to_check = NameStandardValidator(file_path=full_path, bucket_name=None)
    result = path_to_check.validate()
    assert NAME_STANDARD_SUCSESS in result.messages[0]


@pytest.mark.parametrize(
    ("short_name", "file_path_1", "file_path_2", "bucket_name"),
    [
        (
            "stat_reg",
            "person_data_p2022_v1.parquet",
            "bil_data_p2022_v1.parquet",
            "ssb-staging-dapla-felles-data-delt",
        ),
    ],
)
def test_bucket_validation_success(
    short_name,
    file_path_1,
    file_path_2,
    bucket_name,
    monkeypatch,
    tmp_path,
):
    fake_bucket = tmp_path / bucket_name / short_name

    fake_bucket.mkdir(parents=True, exist_ok=True)
    indata_path = fake_bucket / "inndata"
    outdata_path = fake_bucket / "utdata"

    indata_path.mkdir(parents=True, exist_ok=True)
    outdata_path.mkdir(parents=True, exist_ok=True)

    (indata_path / file_path_1).touch()
    (outdata_path / file_path_2).touch()

    validator = NameStandardValidator(file_path=None, bucket_name=bucket_name)
    monkeypatch.setattr(validator, "bucket_directory", fake_bucket)

    results = validator.validate_bucket()

    assert len(results) == 2
    assert results[0].success
    assert all(res.file_path.startswith(str(fake_bucket)) for res in results)


@pytest.mark.parametrize(
    ("file_path_1", "file_path_2", "bucket_name"),
    [
        (
            "_p2022_v1.parquet",
            "bil_data_v1.parquet",
            "ssb-staging-dapla-felles-data-delt",
        ),
    ],
)
def test_bucket_validation_violations(
    file_path_1,
    file_path_2,
    bucket_name,
    monkeypatch,
    tmp_path,
):
    fake_bucket = tmp_path / bucket_name

    fake_bucket.mkdir(parents=True, exist_ok=True)
    indata_path = fake_bucket / "inndata"
    outdata_path = fake_bucket / "utdata"

    indata_path.mkdir(parents=True, exist_ok=True)
    outdata_path.mkdir(parents=True, exist_ok=True)

    (indata_path / file_path_1).touch()
    (outdata_path / file_path_2).touch()

    validator = NameStandardValidator(file_path=None, bucket_name=bucket_name)
    monkeypatch.setattr(validator, "bucket_directory", fake_bucket)

    results = validator.validate_bucket()

    assert len(results) == 2
    assert not results[0].success
    assert MISSING_DATASET_SHORT_NAME in results[1].violations
    assert MISSING_PERIOD in results[0].violations


@pytest.mark.parametrize(
    ("short_name", "indata_file_paths", "processed_file_paths", "bucket_name"),
    [
        (
            "stat_reg",
            [
                "person_data_p2017_p2024_v2/year=2017/data.parquet",
                "person_data_p2017_p2024_v2/year=2018/data.parquet",
            ],
            [
                "person_data_p2017_p2024_v2/year=2017/edited.parquet",
                "person_data_p2017_p2024_v2/year=2018/edited.parquet",
            ],
            "ssb-staging-dapla-felles-data-delt",
        ),
    ],
)
def test_bucket_validation_partitioned_data_success(
    short_name,
    indata_file_paths,
    processed_file_paths,
    bucket_name,
    monkeypatch,
    tmp_path,
):
    fake_bucket = tmp_path / bucket_name / short_name

    fake_bucket.mkdir(parents=True, exist_ok=True)
    indata_path = fake_bucket / "inndata"
    processed_path = fake_bucket / "klargjorte_data"

    indata_path.mkdir(parents=True, exist_ok=True)
    processed_path.mkdir(parents=True, exist_ok=True)

    (indata_path / Path(indata_file_paths[0]).parent).mkdir(parents=True, exist_ok=True)
    (indata_path / Path(indata_file_paths[1]).parent).mkdir(parents=True, exist_ok=True)

    (processed_path / Path(processed_file_paths[0]).parent).mkdir(
        parents=True,
        exist_ok=True,
    )
    (processed_path / Path(processed_file_paths[1]).parent).mkdir(
        parents=True,
        exist_ok=True,
    )

    (indata_path / indata_file_paths[0]).touch()
    (indata_path / indata_file_paths[1]).touch()

    (processed_path / processed_file_paths[0]).touch()
    (processed_path / processed_file_paths[1]).touch()

    validator = NameStandardValidator(file_path=None, bucket_name=bucket_name)
    monkeypatch.setattr(validator, "bucket_directory", fake_bucket)

    results = validator.validate_bucket()

    assert len(results) == 4
    assert all(result.success for result in results)
    assert all(NAME_STANDARD_SUCSESS in result.messages for result in results)
