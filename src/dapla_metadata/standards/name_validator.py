import asyncio
import logging
import os
import re
from collections.abc import AsyncGenerator
from pathlib import Path

from dapla_metadata.datasets.dapla_dataset_path_info import DaplaDatasetPathInfo
from dapla_metadata.standards.utils.constants import FILE_PATH_NOT_CONFIRMED
from dapla_metadata.standards.utils.constants import IGNORED_FOLDERS
from dapla_metadata.standards.utils.constants import MISSING_DATA_STATE
from dapla_metadata.standards.utils.constants import MISSING_DATASET_SHORT_NAME
from dapla_metadata.standards.utils.constants import MISSING_PERIOD
from dapla_metadata.standards.utils.constants import MISSING_SHORT_NAME
from dapla_metadata.standards.utils.constants import NAME_STANDARD_SUCSESS
from dapla_metadata.standards.utils.constants import PATH_IGNORED

logger = logging.getLogger(__name__)


class ValidationResult:
    """Result object for name standard validation."""

    def __init__(
        self,
        success: bool = True,
    ) -> None:
        """Initialize the validatation result."""
        self.success: bool = success
        self.file_path: str | None = None
        self.messages: list[str] = []
        self.violations: list[str] = []

    def add_message(self, message: str) -> None:
        """Add message to list."""
        if message not in self.messages:
            self.messages.append(message)

    def add_violation(self, violation: str) -> None:
        """Add violation to list."""
        if violation not in self.violations:
            self.violations.append(violation)
        if self.success:
            self.success = False

    def __repr__(self) -> str:
        """Representation for debugging."""
        return f"ValidationResult(success={self.success}, file_path={self.file_path}, messages={self.messages}, violations={self.violations})"

    def to_dict(self) -> dict:
        """Return result as a dictionary."""
        return {
            "success": self.success,
            "file_path": self.file_path,
            "messages": self.messages,
            "violations": self.violations,
        }


class NameStandardValidator:
    """Validator for ensuring file names adhere to naming standards."""

    INVALID_PATTERN = r"[^a-zA-Z0-9\./:_-]"

    IGNORED_DATA_STATE_FOLDER = "SOURCE_DATA"

    def __init__(
        self,
        file_path: str | os.PathLike[str] | None,
        bucket_name: Path | str | None,
    ) -> None:
        """Initialize the validator with file path information."""
        self.file_path = Path(file_path).resolve() if file_path else None
        self.bucket_name = bucket_name if bucket_name else None
        self.result: ValidationResult = ValidationResult()
        if self.file_path:
            self.path_info = DaplaDatasetPathInfo(str(file_path))

        if self.bucket_name:
            root = Path("/buckets")
            self.bucket_directory: Path = root / self.bucket_name

    @staticmethod
    def is_invalid_symbols(s: str) -> bool:
        """Return True if string contains illegal symbols.

        Examples:
            >>> NameStandardValidator.is_invalid_symbols("åregang-øre")
            True

            >>> NameStandardValidator.is_invalid_symbols("Azor89")
            False

            >>> NameStandardValidator.is_invalid_symbols("ssbÆ-dapla-example-data-produkt-prod/ledstill/oppdrag/skjema_p2018_p2020_v1")
            True

            >>> NameStandardValidator.is_invalid_symbols("ssb-dapla-example-data-produkt-prod/ledstill/oppdrag/skjema_p2018_p2020_v1")
            False
        """
        return bool(re.search(NameStandardValidator.INVALID_PATTERN, s.strip()))

    def _check_path_existence(self) -> None:
        """Check if the file path exists and add a message if not."""
        if self.file_path and not self.file_path.exists():
            self.result.add_message(
                FILE_PATH_NOT_CONFIRMED,
            )

    def _handle_ignored_folders(
        self,
    ) -> bool:
        """Check dataset state and handle ignored cases.

        Returns:
            bool: True if validation should stop due to ignored dataset state.
        """
        dataset_state = self.path_info.dataset_state
        if dataset_state == self.IGNORED_DATA_STATE_FOLDER:
            self.result.add_message(PATH_IGNORED)
            return True

        if any(
            folder in self.file_path.as_posix().lower()
            for folder in IGNORED_FOLDERS
            if self.file_path is not None
        ):
            self.result.add_message(PATH_IGNORED)
            return True

        return False


def _check_violations(
    file: Path,
) -> list[str]:
    """Check for missing attributes and invalid symbols."""
    path_info = DaplaDatasetPathInfo(file)
    checks = {
        MISSING_SHORT_NAME: path_info.statistic_short_name,
        MISSING_DATA_STATE: path_info.dataset_state,
        MISSING_PERIOD: path_info.contains_data_from,
        MISSING_DATASET_SHORT_NAME: path_info.dataset_short_name,
    }

    return [message for message, value in checks.items() if not value]

    # if self.file_path is not None and self.is_invalid_symbols(
    #     self.file_path.as_posix(),
    # ):
    #     violations.append(INVALID_SYMBOLS)

    # for violation in violations:
    #     self.result.add_violation(violation)


async def validate_file(
    file: Path,
    check_file_exists: bool = False,
) -> ValidationResult:
    """Check for naming standard violations.

    Returns:
        A ValidationResult object containing messages and violations
    """
    # print(f"Validating file: {file}")
    result = ValidationResult()
    result.file_path = str(file)

    if check_file_exists and not file.exists():
        result.add_message(
            FILE_PATH_NOT_CONFIRMED,
        )

    result.violations = await asyncio.get_running_loop().run_in_executor(
        None,
        lambda: _check_violations(file),
    )

    if result.violations:
        result.success = False
    else:
        result.success = True
        result.add_message(
            NAME_STANDARD_SUCSESS,
        )
    return result


async def validate_directory(
    file: Path,
) -> AsyncGenerator[AsyncGenerator | asyncio.Task]:
    """Recursively validate all files in a directory."""
    if file.suffix:
        if file.suffix != ".parquet":
            return
        yield asyncio.create_task(validate_file(file, check_file_exists=True))
    else:
        for obj in await asyncio.get_running_loop().run_in_executor(
            None,
            lambda: file.glob("*"),
        ):
            # print(f"Found {obj}")
            if obj.suffix:
                if obj.suffix != ".parquet":
                    continue
                yield asyncio.create_task(validate_file(obj), name=obj.name)

            else:
                yield validate_directory(obj)
