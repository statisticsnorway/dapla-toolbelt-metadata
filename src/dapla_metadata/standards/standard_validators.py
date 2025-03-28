import asyncio
import os
import time
from collections.abc import AsyncGenerator

from dapla_metadata.datasets.utility.utils import normalize_path
from dapla_metadata.standards.name_validator import ValidationResult
from dapla_metadata.standards.name_validator import validate_directory


async def check_naming_standard(
    file_path: os.PathLike[str],
) -> list[ValidationResult]:
    """Check whether a given path follows the SSB naming standard.

    This function checks whether the provided `file_path` and subdirectories thereof comply
    with the naming standard. Currently we only examine '.parquet' files. Other files are ignored.

    Args:
        file_path: The path to a bucket, directory, or specific file to validate.
                This can be in the following forms:
                  - A bucket URL in the form 'gs://ssb-dapla-felles-data-produkt-test'
                  - An absolute path to a mounted bucket in the form '/buckets/produkt'
                  - Any subdirectory or file thereof
                We also accept paths which don't yet exist so that you can test if a path will comply.

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
    results = []
    tasks = [t async for t in validate_directory(normalize_path(file_path))]
    start_time = time.time()
    while time.time() < start_time + (2 * 60):
        for item in tasks:
            if isinstance(item, AsyncGenerator):
                # Drill down into lower directories to get the validation tasks from them
                tasks.remove(item)
                tasks.extend(
                    [t async for t in item],
                )
            elif isinstance(item, asyncio.Task):
                if item.done():
                    print(f"Validated {item.get_name()}")
                    tasks.remove(item)
                    results.append(item.result())
        if len(tasks) == 0:
            print("No tasks left")
            break
        if all(isinstance(t, asyncio.Task) for t in tasks) and all(
            t.done() for t in tasks
        ):
            print("All tasks complete")
            break
        await asyncio.sleep(1)

    return results
