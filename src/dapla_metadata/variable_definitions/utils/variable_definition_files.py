"""Generate structured YAML files from Pydantic models with Norwegian descriptions as comments."""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import cast

import pytz
from pydantic.config import JsonDict
from ruamel.yaml import YAML
from ruamel.yaml import CommentedMap

from dapla_metadata.variable_definitions.generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions.utils.constants import DEFAULT_TEMPLATE
from dapla_metadata.variable_definitions.utils.constants import HEADER
from dapla_metadata.variable_definitions.utils.constants import MACHINE_GENERATED_FIELDS
from dapla_metadata.variable_definitions.utils.constants import NORWEGIAN_DESCRIPTIONS
from dapla_metadata.variable_definitions.utils.constants import OWNER_FIELD_NAME
from dapla_metadata.variable_definitions.utils.constants import TEMPLATE_HEADER
from dapla_metadata.variable_definitions.utils.constants import (
    TEMPLATE_SECTION_HEADER_MACHINE_GENERATED,
)
from dapla_metadata.variable_definitions.utils.constants import (
    TEMPLATE_SECTION_HEADER_OWNER,
)
from dapla_metadata.variable_definitions.utils.constants import (
    TEMPLATE_SECTION_HEADER_STATUS,
)
from dapla_metadata.variable_definitions.utils.constants import VARIABLE_DEFINITIONS_DIR
from dapla_metadata.variable_definitions.utils.constants import (
    VARIABLE_STATUS_FIELD_NAME,
)
from dapla_metadata.variable_definitions.utils.descriptions import (
    apply_norwegian_descriptions_to_model,
)
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition


def _model_to_yaml_with_comments(
    model_instance: CompletePatchOutput | VariableDefinition,
    file_name: str,
    start_comment: str,
    custom_directory: str | Path | None = None,
) -> Path:
    """Convert a model instance to a structured YAML file with Norwegian descriptions as comments.

    Adds Norwegian descriptions to the model, organizes fields into sections, and saves
    the YAML file with a structured format and timestamped filename.

    Args:
        model_instance: The model instance to convert.
        file_name: Name of the generated YAML file.
        start_comment: Comment at the top of the file.
        custom_directory: Optional directory to save the file.

    Returns:
        Path: File path of the generated YAML file.
    """
    yaml = _configure_yaml()

    # Apply new fields to model
    apply_norwegian_descriptions_to_model(CompletePatchOutput)
    apply_norwegian_descriptions_to_model(VariableDefinition)

    data = model_instance.model_dump()  # Convert Pydantic model instance to dictionary

    # One CommentMap for each section in the yaml file
    machine_generated_map = CommentedMap()
    commented_map = CommentedMap()
    status_map = CommentedMap()
    owner_map = CommentedMap()

    # Loop through all fields in the model and populate the commented maps
    for field_name, value in data.items():
        if field_name == VARIABLE_STATUS_FIELD_NAME:
            _populate_commented_map(field_name, value, status_map, model_instance)
        elif field_name == OWNER_FIELD_NAME:
            _populate_commented_map(field_name, value, owner_map, model_instance)
        elif field_name in MACHINE_GENERATED_FIELDS:
            _populate_commented_map(
                field_name,
                value,
                machine_generated_map,
                model_instance,
            )
        elif field_name not in {VARIABLE_STATUS_FIELD_NAME, OWNER_FIELD_NAME}:
            _populate_commented_map(field_name, value, commented_map, model_instance)

    base_path = (
        _get_variable_definitions_dir()
        if custom_directory is None
        else _get_custom_directory(custom_directory)
    )

    file_path = base_path / file_name

    # It is important to preserve the order of the yaml dump operations when writing to file
    # so that the file is predictable for the user
    with file_path.open("w", encoding="utf-8") as file:
        commented_map.yaml_set_start_comment(start_comment)
        yaml.dump(commented_map, file)

        status_map.yaml_set_start_comment(TEMPLATE_SECTION_HEADER_STATUS)
        yaml.dump(status_map, file)

        owner_map.yaml_set_start_comment(TEMPLATE_SECTION_HEADER_OWNER)
        yaml.dump(owner_map, file)

        machine_generated_map.yaml_set_start_comment(
            TEMPLATE_SECTION_HEADER_MACHINE_GENERATED,
        )
        yaml.dump(machine_generated_map, file)
    return file_path


def create_variable_yaml(
    model_instance: VariableDefinition,
    custom_directory: Path | None = None,
) -> Path:
    """Creates a yaml file for an existing variable definition."""
    file_name = _create_file_name(
        "variable_definition",
        _get_current_time(),
        _get_shortname(model_instance),
        _get_variable_definition_id(model_instance),
    )

    return _model_to_yaml_with_comments(
        model_instance,
        file_name,
        HEADER,
        custom_directory=custom_directory,
    )


def create_template_yaml(
    model_instance: CompletePatchOutput = DEFAULT_TEMPLATE,
    custom_directory: Path | None = None,
) -> Path:
    """Creates a template yaml file for a new variable definition."""
    file_name = _create_file_name(
        "variable_definition_template",
        _get_current_time(),
    )

    return _model_to_yaml_with_comments(
        model_instance,
        file_name,
        TEMPLATE_HEADER,
        custom_directory=custom_directory,
    )


def _populate_commented_map(
    field_name: str,
    value: str,
    commented_map: CommentedMap,
    model_instance: CompletePatchOutput | VariableDefinition,
) -> None:
    """Add data to a CommentedMap."""
    commented_map[field_name] = value
    description: JsonDict = cast(JsonDict, model_instance.model_fields[field_name].json_schema_extra[NORWEGIAN_DESCRIPTIONS])  # type: ignore[index]
    if description is not None:
        commented_map.yaml_set_comment_before_after_key(
            field_name,
            before=description,
        )


def _create_file_name(
    base_name: str,
    time_object: str,
    short_name: str | None = None,
    variable_definition_id: str | None = None,
) -> str:
    """Return file name with dynamic timestamp, and shortname and id if available."""
    return (
        "_".join(
            filter(
                None,
                [
                    base_name,
                    short_name,
                    variable_definition_id,
                    time_object,
                ],
            ),
        )
        + ".yaml"
    )


def _get_current_time() -> str:
    """Return a string format date now for filename."""
    timezone = pytz.timezone("Europe/Oslo")
    current_datetime = datetime.now(timezone).strftime("%Y-%m-%dT%H-%M-%S")
    return str(current_datetime)


def _get_workspace_dir() -> Path:
    """Determine the workspace directory."""
    try:
        # Attempt to get the directory from the environment variable
        workspace_dir = Path(os.environ["WORKSPACE_DIR"])

        # Check if the directory exists and is actually a directory
        if not workspace_dir.exists():
            msg = f"Directory '{workspace_dir}' does not exist."
            raise FileNotFoundError(msg)
        if not workspace_dir.is_dir():
            msg = f"'{workspace_dir}' is not a directory."
            raise NotADirectoryError(msg)

    except KeyError:
        # Fallback: search for a directory called 'work' starting from the current directory
        current_dir = Path.cwd()
        while current_dir != current_dir.parent:
            potential_workspace = current_dir / "work"
            if potential_workspace.exists() and potential_workspace.is_dir():
                workspace_dir = potential_workspace
                break
            current_dir = current_dir.parent
        else:
            # Raise an error if 'work' directory is not found
            msg = "'work' directory not found and env WORKSPACE_DIR is not set."
            raise FileNotFoundError(msg)

    return workspace_dir


def _get_custom_directory(custom_directory: str) -> Path:
    custom_directory = Path(custom_directory).resolve()

    if custom_directory.suffix:
        exception_message = (
            f"Expected a directory but got a file name: %{custom_directory.name}",
        )
        raise ValueError(exception_message)

    if custom_directory.exists() and not custom_directory.is_dir():
        exception_message = (f"Path exists but is not a directory: {custom_directory}",)
        raise NotADirectoryError(exception_message)

    dir_name = custom_directory.name
    # Windows-specific checks
    if sys.platform.startswith("win"):
        invalid_chars = r'[<>:"/\\|?*]'
        reserved_names = {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }

        if any(char in dir_name for char in invalid_chars):
            exception_message = f"Invalid character in directory name: {dir_name}"
            raise ValueError(exception_message)

        if dir_name.upper() in reserved_names:
            exception_message = (
                f"Directory name '{dir_name}' is a reserved system name."
            )
            raise ValueError(exception_message)

        if dir_name.endswith((" ", ".")):
            exception_message = "Windows directory error."
            raise ValueError(exception_message)

    # Linux/macOS checks
    elif sys.platform.startswith("linux") or sys.platform.startswith("darwin"):
        if "/" in dir_name or "\0" in dir_name:
            exception_message = f"Invalid character in directory name: {dir_name}"
            raise ValueError(exception_message)
    max_length = 255
    if len(dir_name) > max_length:
        exception_message = (
            "Directory name exceeds the maximum length of 255 characters."
        )
        raise ValueError(exception_message)

    try:
        custom_directory.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        exception_message = (
            f"Insufficient permissions to create directory: {custom_directory}",
        )
        raise PermissionError(exception_message) from e
    except OSError as e:
        exception_message = f"Failed to create directory {custom_directory}: {e!s}"
        raise OSError(exception_message) from e

    return custom_directory


def _get_variable_definitions_dir():
    """Get or create the variable definitions directory inside the workspace."""
    workspace_dir = _get_workspace_dir()
    folder_path = workspace_dir / VARIABLE_DEFINITIONS_DIR
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path


def _configure_yaml() -> YAML:
    yaml = YAML()  # Use ruamel.yaml library
    yaml.default_flow_style = False  # Ensures pretty YAML formatting

    yaml.representer.add_representer(
        VariableStatus,
        lambda dumper, data: dumper.represent_scalar(
            "tag:yaml.org,2002:str",
            data.value,
        ),
    )

    return yaml


def _get_shortname(
    model_instance: CompletePatchOutput | VariableDefinition,
) -> str | None:
    return model_instance.short_name


def _get_variable_definition_id(
    model_instance: CompletePatchOutput | VariableDefinition,
) -> str | None:
    return model_instance.id
