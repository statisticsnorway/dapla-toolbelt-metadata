import os
from datetime import datetime
from pathlib import Path

import pytz
from ruamel.yaml import YAML
from ruamel.yaml import CommentedMap

from dapla_metadata.variable_definitions.complete_patch_output import DEFAULT_TEMPLATE
from dapla_metadata.variable_definitions.generated.vardef_client.models.complete_response import (
    CompleteResponse,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions.utils.constants import HEADER
from dapla_metadata.variable_definitions.utils.constants import MACHINE_GENERATED_FIELDS
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


def _model_to_yaml_with_comments(
    model_instance: CompleteResponse,
    file_name: str,
    start_comment: str,
    custom_directory: Path | None = None,
) -> Path:
    """Convert a model instance into a structured YAML file with comments.

    This function:
    - Extracts data from a model instance.
    - Adds descriptive comments above each field.
    - Organizes the YAML output into logical sections with meaningful headers.
    - Saves the YAML content to a file, ensuring a predictable structure.

    The resulting file is named with a fixed filename and a timestamp to avoid overwriting previous templates.

    Args:
        model_instance:
            The instance to convert. Defaults to `DEFAULT_TEMPLATE`.
        file_name:
            The file name that the yaml file will get.
        start_comment:
            The comment at the top of the generated yaml file.
        custom_directory:
            Optional directory where to save the template. defaults to None

    Returns:
        Path: The file path of the generated YAML file.
    """
    yaml = _configure_yaml()

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
        else custom_directory
    )

    if custom_directory is not None:
        base_path.mkdir(parents=True, exist_ok=True)

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


def _read_variable_definition_file(file_path: os.PathLike) -> dict:
    raise NotImplementedError


def _find_latest_file_for_id(variable_definition_id: str) -> Path:
    raise NotImplementedError


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
    description = model_instance.model_fields[field_name].description
    if description:
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
            msg = f"WORKSPACE_DIR '{workspace_dir}' does not exist."
            raise FileNotFoundError(msg)
        if not workspace_dir.is_dir():
            msg = f"WORKSPACE_DIR '{workspace_dir}' is not a directory."
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
