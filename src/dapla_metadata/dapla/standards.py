from os import PathLike
from pathlib import Path
from typing import Literal
from cloudpathlib import CloudPath
from dapla_metadata.dapla.name_validator import NameStandardValidator

def check_naming_standard(file_path: Path | CloudPath | PathLike) -> str | list:
    """Check a given path."""
    naming_validator = NameStandardValidator(file_path)
    return naming_validator.validate
    