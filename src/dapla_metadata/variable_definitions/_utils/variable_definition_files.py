"""Utilities for writing and reading existing variable definition files."""

import logging
from os import PathLike
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel
from ruamel.yaml import YAML

from dapla_metadata.variable_definitions._generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions._utils.constants import HEADER
from dapla_metadata.variable_definitions._utils.files import _create_file_name
from dapla_metadata.variable_definitions._utils.files import _get_current_time
from dapla_metadata.variable_definitions._utils.files import (
    _model_to_yaml_with_comments,
)

logger = logging.getLogger(__name__)


T = TypeVar("T", bound=BaseModel)


def create_variable_yaml(
    model_instance: CompleteResponse,
    custom_directory: Path | None = None,
) -> Path:
    """Creates a yaml file for an existing variable definition."""
    file_name = _create_file_name(
        "variable_definition",
        _get_current_time(),
        model_instance.short_name,
        model_instance.id,
    )

    return _model_to_yaml_with_comments(
        model_instance,
        file_name,
        HEADER,
        custom_directory=custom_directory,
    )


def _read_variable_definition_file(file_path: Path) -> dict:
    yaml = YAML()

    logger.debug("Full path to variable definition file %s", file_path)
    logger.info("Reading from '%s'", file_path.name)
    with file_path.open(encoding="utf-8") as f:
        return yaml.load(f)


def _read_file_to_model(
    file_path: PathLike[str] | None,
    model_class: type[T],
) -> T:
    """Read from a variable definition file into the given Pydantic model.

    Args:
        file_path (PathLike[str]): The path to the file to read in.
        model_class (type[T]): The model to instantiate. Must inherit from Pydantic's BaseModel.

    Raises:
        TypeError: If no file path could be deduced.
        FileNotFoundError: If we could not instantiate the model.

    Returns:
        T: BaseModel: The instantiated Pydantic model
    """
    try:
        file_path = Path(
            # type incongruence (i.e. None) is handled by catching the exception
            file_path,  # type: ignore [arg-type]
        )
    except TypeError as e:
        msg = "Could not deduce a path to the file. Please supply a path to the yaml file you wish to submit with the `file_path` parameter."
        raise FileNotFoundError(
            msg,
        ) from e
    model = model_class.from_dict(  # type:ignore [attr-defined]
        _read_variable_definition_file(
            file_path,
        ),
    )

    if model is None:
        msg = f"Could not read data from {file_path}"
        raise FileNotFoundError(msg)

    return model
