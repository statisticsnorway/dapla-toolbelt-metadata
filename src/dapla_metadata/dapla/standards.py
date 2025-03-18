from os import PathLike
import os
from pathlib import Path
from cloudpathlib import CloudPath
from dapla_metadata.dapla.name_validator import NameStandardValidator

def check_naming_standard(file_path: str | os.PathLike[str]) -> str | list:
    """Check a given path."""
    naming_validator = NameStandardValidator(file_path)
    return naming_validator.validate
    