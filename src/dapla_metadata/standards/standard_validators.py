import asyncio
import os
from collections.abc import AsyncGenerator

from dapla_metadata.datasets.utility.utils import normalize_path
from dapla_metadata.standards.name_validator import ValidationResult
from dapla_metadata.standards.name_validator import validate_directory


async def check_naming_standard(
    file_path: os.PathLike[str],
) -> ValidationResult | list[ValidationResult]:
    """Check a given path following ssb name standard.

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
    loop = asyncio.get_event_loop()
    loop.set_task_factory(asyncio.eager_task_factory)

    def get_results(
        item: asyncio.Task | AsyncGenerator,
    ) -> list[ValidationResult]:
        if isinstance(item, asyncio.Task):
            return list(item.result)
        return [t.result for t in item]

    results = []
    finished = False
    initial = [t async for t in validate_directory(normalize_path(file_path))]
    while not finished:
        for item in initial:
            if isinstance(item, AsyncGenerator):
                initial.remove(item)
                initial.extend(
                    [t async for t in item],
                )
            elif isinstance(item, asyncio.Task):
                initial.remove(item)
                results.append(item.result())
            else:
                print(f"Skipping {item}")
        if not any(isinstance(i, AsyncGenerator) for i in initial):
            finished = True

    return results
