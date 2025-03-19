import os

from dapla_metadata.standards.name_validator import NameStandardValidator


def check_naming_standard(file_path: str | os.PathLike[str]) -> str | list:
    """Check a given path following ssb name standard."""
    naming_validator = NameStandardValidator(file_path)
    return naming_validator.validate
