from pathlib import Path
from cloudpathlib import CloudPath
from dapla_metadata.dapla.name_validator import NameStandardValidator

def check_naming_standard(file_path: Path | CloudPath):
    """Check a given path."""
    return NameStandardValidator(file_path).validate()