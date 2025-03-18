
from pathlib import Path
from cloudpathlib import CloudPath
from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo

def check_naming_standard(file_path: Path | CloudPath)-> bool:
    """Check."""
    dataset_path = DaplaDatasetPathInfo(file_path)
    if dataset_path.path_complies_with_naming_standard():
        return True
    return False