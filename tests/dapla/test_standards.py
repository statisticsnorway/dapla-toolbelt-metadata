
import datetime
from pathlib import Path

import pytest
from dapla_metadata.dapla.standards import check_naming_standard
from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo


def test_file_path_does_not_follow_naming_standard():
    result = check_naming_standard('tests/dataset/klargjorte_data/arbmark/resources/person_data_v1.parquet')
    assert result == ['Missing valid from']
    
def test_file_path_follow_naming_standard():
    result = check_naming_standard('buckets/dataset/klargjorte_data/arbmark/resources/person_data_p2021-12-31_p2021-12-31_v1.parquet')
    assert result == "Your files comply to SSB naming standard"
    
def test_dapla_dataset_path():
    dataset_path = DaplaDatasetPathInfo('buckets/dataset/klargjorte_data/arbmark/resources/person_data_p2021-12-31_p2021-12-31_v1.parquet')
    assert dataset_path.bucket_name is None
    assert dataset_path.contains_data_from == datetime.date(2021,12,31)
    assert dataset_path.path_complies_with_naming_standard() is True
    
def test_dapla_dataset_path_not():
    dataset_path = DaplaDatasetPathInfo('tests/dataset/klargjorte_data/arbmark/resources/person_data_v1.parquet')
    assert dataset_path.path_complies_with_naming_standard() is False
    

@pytest.mark.parametrize(
    ("data"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/person_data_p2022_v1.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/person_data_p2021_v3.parquet",
        "buckets/produkt/test-2/person_testdata_p2021-12-31_p2021-12-31_v1.parquet"
    ],
)
def test_invalid_directory(data: str):
    assert check_naming_standard(data) == ['Missing folder for data', 'Missing folder short name',]
 
@pytest.mark.parametrize(
    ("data"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_v1.parquet",
    ],
)
def test_invalid_date(data: str):
    assert check_naming_standard(data) == ['Missing valid from']

#"gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021.parquet",

@pytest.mark.parametrize(
    ("data"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/person_data_v1.parquet",
    ],
)
def test_invalid_date_and_dir(data: str):
    assert check_naming_standard(data) == [
        'Missing folder for data',
        'Missing folder short name',
        'Missing valid from'
] 
        
@pytest.mark.parametrize(
    ("data"),
    [
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_v2.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/person_data_p2021_p2022_v2.parquet",
        "gs://ssb-staging-dapla-felles-data-delt/datadoc/utdata/undermappe/person_data_p2021_v2.parquet",
    ],
)
def test_valid_names(data: str):
    assert check_naming_standard(data) == "Your files comply to SSB naming standard"


@pytest.mark.parametrize(
    ("data"),
    [
        "buckets/inndata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "buckets/klargjorte-data/person_testdata_p2021-12-31_p2021-12-31_v1.parquet",
        "buckets/utdata/person_testdata_p2021-12-31_p2021-12-31_v1.parquet"
    ],
)
def test_names_buckets(data: str):
    assert check_naming_standard(data) == "Your files comply to SSB naming standard"

@pytest.mark.parametrize(
    ("data"),
    [
        "ssb-dapla-example-data-produkt-prod/ledstill/inndata/skjema_p2018_p2020_v1"
    ],
)
def test_names_partioned(data: str):
    assert check_naming_standard(data) == "Your files comply to SSB naming standard"
    
@pytest.mark.parametrize(
    ("data"),
    [
        "ssb-dapla-example-data-produkt-prod/ledstill/oppdrag/skjema_p2018_p2020_v1"
    ],
)
def test_names_optional_dir(data: str):
    assert check_naming_standard(data) == ['Missing folder for data', 'Missing folder short name',]
    
@pytest.mark.parametrize(
    ("data"),
    [
        Path("ssb-dapla-example-data-produkt-prod/ledstill/temp/skjema_p2018_p2020_v1")
    ],
)
def test_names_temp_dir(data: str):
    assert check_naming_standard(data) == ['Missing folder for data', 'Missing folder short name',]
