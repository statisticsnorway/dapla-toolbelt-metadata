"""Generate structured YAML files from Pydantic models with Norwegian descriptions as comments."""

import logging
from datetime import datetime
from pathlib import Path
from typing import cast

import pytz
from pydantic.config import JsonDict
from ruamel.yaml import YAML
from ruamel.yaml import CommentedMap

from dapla_metadata.variable_definitions import config
from dapla_metadata.variable_definitions.complete_patch_output import DEFAULT_TEMPLATE
from dapla_metadata.variable_definitions.exceptions import VardefFileError
from dapla_metadata.variable_definitions.generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.variable_status import (
    VariableStatus,
)
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

logger = logging.getLogger(__name__)


def _model_to_yaml_with_comments(
    model_instance: CompleteResponse,
    file_name: str,
    start_comment: str,
    custom_directory: Path | None = None,
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
        Path: The file path of the generated YAML file.
    """
    yaml = _configure_yaml()

    from dapla_metadata.variable_definitions.variable_definition import (
        CompletePatchOutput,
    )
    from dapla_metadata.variable_definitions.variable_definition import (
        VariableDefinition,
    )

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
        else _validate_and_create_directory(custom_directory)
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


def create_template_yaml(
    model_instance: CompleteResponse = DEFAULT_TEMPLATE,
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
    model_instance: CompleteResponse,
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
    workspace_dir = config.get_workspace_dir()

    if workspace_dir is None:
        msg = "WORKSPACE_DIR is not set in the configuration."
        raise VardefFileError(msg)
    workspace_dir_path: Path
    if workspace_dir is not None:
        workspace_dir_path = Path(workspace_dir)
        workspace_dir_path.resolve()

        if not workspace_dir_path.exists():
            msg = f"Directory '{workspace_dir_path}' does not exist."
            raise FileNotFoundError(msg)

        if not workspace_dir_path.is_dir():
            msg = f"'{workspace_dir_path}' is not a directory."
            raise NotADirectoryError(msg)
        logger.debug("'WORKSPACE_DIR' value: %s", workspace_dir)
    return workspace_dir_path


def _validate_and_create_directory(custom_directory: Path) -> Path:
    """Ensure that the given path is a valid directory, creating it if necessary.

    Args:
        custom_directory (Path): The target directory path.

    Returns:
        Path: The resolved absolute path of the directory.

    Raises:
        ValueError: If the provided path has a file suffix, indicating a file name instead of a directory.
        NotADirectoryError: If the path exists but is not a directory.
        PermissionError: If there are insufficient permissions to create the directory.
        OSError: If an OS-related error occurs while creating the directory.
    """
    custom_directory = Path(custom_directory).resolve()

    if custom_directory.suffix:
        msg = f"Expected a directory but got a file name: %{custom_directory.name}"
        raise ValueError(msg)

    if custom_directory.exists() and not custom_directory.is_dir():
        msg = f"Path exists but is not a directory: {custom_directory}"
        raise NotADirectoryError(msg)

    try:
        custom_directory.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        msg = f"Insufficient permissions to create directory: {custom_directory}"
        raise PermissionError(msg) from e
    except OSError as e:
        msg = f"Failed to create directory {custom_directory}: {e!s}"
        raise OSError(msg) from e

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
