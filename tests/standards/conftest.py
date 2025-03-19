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
