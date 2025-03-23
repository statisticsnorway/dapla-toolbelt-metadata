from pathlib import Path

from cloudpathlib import CloudPath

from dapla_metadata.standards.name_validator import NameStandardValidator
from dapla_metadata.standards.name_validator import ValidationResult


# -> str | list:
def check_naming_standard(
    file_path: Path | CloudPath | None,
    bucket_name: str | None = None,
) -> ValidationResult | list:
    """Check a given path following ssb name standard."""
    naming_validator = NameStandardValidator(
        file_path=file_path,
        bucket_name=bucket_name,
    )
    if not file_path:
        return naming_validator.validate_bucket()
    return naming_validator.validate()
