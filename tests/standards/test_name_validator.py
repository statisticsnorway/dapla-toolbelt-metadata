import pytest

from dapla_metadata.standards.name_validator import BucketNameValidator
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
    path_to_check = NameStandardValidator(file_path=full_path)
    result = path_to_check.validate()
    assert NAME_STANDARD_SUCSESS in result.messages[0]


@pytest.mark.parametrize(
    ("short_name", "file_paths", "bucket_name"),
    [
        (
            "stat_reg",
            ["person_data_p2022_v1.parquet", "bil_data_p2022_v1.parquet"],
            "ssb-staging-dapla-felles-data-delt",
        ),
    ],
)
def test_bucket_validation_success(
    short_name,
    file_paths,
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

    (indata_path / file_paths[0]).touch()
    (outdata_path / file_paths[1]).touch()

    validator = BucketNameValidator(bucket_name=bucket_name)
    monkeypatch.setattr(validator, "bucket_directory", fake_bucket)

    results = validator.validate()

    assert len(results) == 2
    assert results[0].success


@pytest.mark.parametrize(
    ("file_paths", "bucket_name"),
    [
        (
            ["_p2022_v1.parquet", "bil_data_v1.parquet"],
            "ssb-staging-dapla-felles-data-delt",
        ),
    ],
)
def test_bucket_validation_violations(
    file_paths,
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

    (indata_path / file_paths[0]).touch()
    (outdata_path / file_paths[1]).touch()

    validator = BucketNameValidator(bucket_name=bucket_name)
    monkeypatch.setattr(validator, "bucket_directory", fake_bucket)

    results = validator.validate()

    assert len(results) == 2
    assert not results[0].success
    assert MISSING_DATASET_SHORT_NAME in results[1].violations
    assert MISSING_PERIOD in results[0].violations
