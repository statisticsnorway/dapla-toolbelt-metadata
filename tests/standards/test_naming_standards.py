
from dapla_metadata.standards.naming_standards import validate_bucket_name


def test_file_path_follow_naming_standard():
    result = validate_bucket_name('tests/dataset/klargjorte_data/arbmark/resources/person_data_v1.parquet')
    assert result is False