from pathlib import Path

from cloudpathlib import CloudPath

from dapla_metadata.standards.name_validator import BucketNameValidator
from dapla_metadata.standards.name_validator import NameStandardValidator
from dapla_metadata.standards.name_validator import ValidationResult


def check_naming_standard(
    file_path: Path | CloudPath | None,
    bucket_name: str | None = None,
) -> ValidationResult | list[ValidationResult]:
    """Check a given path or bucket following ssb name standard.

    This function checks whether the provided `file_path` or all files within
    the specified `bucket` adhere to the SSB name standard.

    Args:
        file_path: The path to a specific file to validate.
        bucket_name: The name of the bucket containing files to be validated.

    Returns:
        ValidationResult(s): An object or list of objects containing validation results,
        including success status, checked file path, messages, and any detected violations.

    Examples:
        >>> check_naming_standard(file_path=Path("/data/example_file.parquet")).success
        False

        >>> check_naming_standard(file_path=Path("buckets/produkt/datadoc/utdata/person_data_p2021_v2.parquet")).success
        True
    """
    naming_validator: BucketNameValidator | NameStandardValidator
    if bucket_name:
        naming_validator = BucketNameValidator(bucket_name=bucket_name)
    elif file_path:
        naming_validator = NameStandardValidator(file_path=file_path)
    return naming_validator.validate()
