"""Validate content of data buckets."""

from pathlib import Path
from cloudpathlib import CloudPath
from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo

def validate_bucket_name(file_path: Path | CloudPath)-> bool:
    """Check."""
    return False