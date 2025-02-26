import functools
from collections.abc import Callable
from pathlib import Path
from unittest.mock import patch

import pytest

from dapla_metadata._shared.config import DAPLA_GROUP_CONTEXT
from dapla_metadata.variable_definitions._client import VardefClient
from dapla_metadata.variable_definitions.exceptions import VardefClientException
from dapla_metadata.variable_definitions.exceptions import VariableNotFoundError
from dapla_metadata.variable_definitions.generated.vardef_client.api.variable_definitions_api import (
    VariableDefinitionsApi,
)
from dapla_metadata.variable_definitions.generated.vardef_client.configuration import (
    Configuration,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.draft import (
    Draft,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.patch import (
    Patch,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.update_draft import (
    UpdateDraft,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.validity_period import (
    ValidityPeriod,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions.vardef import Vardef
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition
from tests.utils.constants import NOT_FOUND_STATUS
from tests.utils.constants import VARDEF_EXAMPLE_ACTIVE_GROUP
from tests.utils.constants import VARDEF_EXAMPLE_DATE
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID
from tests.utils.constants import VARDEF_EXAMPLE_INVALID_ID
from tests.utils.constants import VARDEF_EXAMPLE_SHORT_NAME
from tests.variable_definitions.conftest import sample_variable_definition
from tests.variable_definitions.conftest import unknown_variable_definition

PATCH_ID = 2


def test_list_variable_definitions(client_configuration: Configuration):
    VardefClient.set_config(client_configuration)
    assert Vardef.list_variable_definitions() == []


def test_list_variable_definitions_with_date_of_validity(
    client_configuration: Configuration,
):
    VardefClient.set_config(client_configuration)
    assert isinstance(
        Vardef.list_variable_definitions(date_of_validity=VARDEF_EXAMPLE_DATE)[0],
        CompletePatchOutput,
    )


def test_get_variable_definition_by_id(client_configuration: Configuration):
    VardefClient.set_config(client_configuration)
    landbak = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak, VariableDefinition)
    assert landbak.classification_reference == "91"


def test_get_variable_definition_by_short_name(client_configuration: Configuration):
    VardefClient.set_config(client_configuration)
    landbak = Vardef.get_variable_definition_by_shortname(
        short_name=VARDEF_EXAMPLE_SHORT_NAME,
    )
    assert isinstance(landbak, VariableDefinition)
    assert landbak.classification_reference == "91"


def test_get_variable_definition_by_nonexistent_short_name(
    client_configuration: Configuration,
):
    VardefClient.set_config(client_configuration)
    short_name = "nonexistent"
    mock_response = []
    with patch.object(
        VariableDefinitionsApi,
        "list_variable_definitions",
        return_value=mock_response,
    ), pytest.raises(
        VariableNotFoundError,
        match=f"Variable with short name {short_name} not found",
    ):
        Vardef.get_variable_definition_by_shortname(short_name=short_name)


def test_get_variable_definition_multiple_variables_returned(
    client_configuration: Configuration,
):
    VardefClient.set_config(client_configuration)
    short_name = "multiple"
    mock_response = ["variable", "variable"]
    with patch.object(
        VariableDefinitionsApi,
        "list_variable_definitions",
        return_value=mock_response,
    ), pytest.raises(
        VariableNotFoundError,
        match=f"Lookup by short name {short_name} found multiple variables which should not be possible",
    ):
        Vardef.get_variable_definition_by_shortname(short_name=short_name)


@pytest.mark.parametrize(
    ("method"),
    [
        functools.partial(
            Vardef.get_variable_definition_by_id,
            variable_definition_id=VARDEF_EXAMPLE_INVALID_ID,
        ),
        unknown_variable_definition().list_validity_periods,
        unknown_variable_definition().list_patches,
        functools.partial(sample_variable_definition().get_patch, patch_id=244),
    ],
)
def test_not_found(
    monkeypatch: pytest.MonkeyPatch,
    client_configuration: Configuration,
    method: Callable,
):
    monkeypatch.setenv(DAPLA_GROUP_CONTEXT, VARDEF_EXAMPLE_ACTIVE_GROUP)
    VardefClient.set_config(client_configuration)
    with pytest.raises(VardefClientException) as e:
        method()
    assert e.value.status == NOT_FOUND_STATUS
    assert e.value.detail == "Not found"
    assert str(e.value) == "Status 404: Not found"


def test_list_patches(client_configuration: Configuration):
    VardefClient.set_config(client_configuration)
    landbak = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.list_patches()[0], CompletePatchOutput)


def test_get_patch(client_configuration: Configuration):
    VardefClient.set_config(client_configuration)
    landbak = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.get_patch(1), CompletePatchOutput)


def test_list_validity_periods(client_configuration: Configuration):
    VardefClient.set_config(client_configuration)
    landbak = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.list_validity_periods()[0], CompletePatchOutput)


def test_create_draft(
    monkeypatch: pytest.MonkeyPatch,
    client_configuration: Configuration,
    draft: Draft,
):
    monkeypatch.setenv(DAPLA_GROUP_CONTEXT, VARDEF_EXAMPLE_ACTIVE_GROUP)
    VardefClient.set_config(client_configuration)
    my_draft = Vardef.create_draft(
        draft=draft,
    )
    assert isinstance(my_draft, CompletePatchOutput)
    assert my_draft.id is not None
    assert my_draft.patch_id == 1
    assert my_draft.variable_status == VariableStatus.DRAFT


def test_migrate_from_vardok(
    monkeypatch: pytest.MonkeyPatch,
    client_configuration: Configuration,
):
    monkeypatch.setenv(DAPLA_GROUP_CONTEXT, VARDEF_EXAMPLE_ACTIVE_GROUP)
    VardefClient.set_config(client_configuration)
    my_draft = Vardef.migrate_from_vardok(
        vardok_id="1607",
    )
    assert isinstance(my_draft, CompletePatchOutput)
    assert my_draft.id is not None
    assert my_draft.patch_id == 1
    assert my_draft.variable_status == VariableStatus.DRAFT


def test_update_draft(
    monkeypatch: pytest.MonkeyPatch,
    client_configuration: Configuration,
    update_draft: UpdateDraft,
):
    monkeypatch.setenv(DAPLA_GROUP_CONTEXT, VARDEF_EXAMPLE_ACTIVE_GROUP)
    VardefClient.set_config(client_configuration)
    my_draft = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(my_draft.update_draft(update_draft), CompletePatchOutput)


def test_delete_draft(
    monkeypatch: pytest.MonkeyPatch,
    client_configuration: Configuration,
):
    monkeypatch.setenv(DAPLA_GROUP_CONTEXT, VARDEF_EXAMPLE_ACTIVE_GROUP)
    VardefClient.set_config(client_configuration)
    my_draft = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert my_draft.id is not None
    result = my_draft.delete_draft()
    assert result == f"Variable {VARDEF_EXAMPLE_DEFINITION_ID} safely deleted"


def test_create_patch(
    monkeypatch: pytest.MonkeyPatch,
    client_configuration: Configuration,
    patch: Patch,
    variable_definition: VariableDefinition,
):
    monkeypatch.setenv(DAPLA_GROUP_CONTEXT, VARDEF_EXAMPLE_ACTIVE_GROUP)
    VardefClient.set_config(client_configuration)
    my_variable = variable_definition
    assert my_variable.patch_id == 1
    created_patch = my_variable.create_patch(
        patch=patch,
        valid_from=VARDEF_EXAMPLE_DATE,
    )
    assert isinstance(
        created_patch,
        CompletePatchOutput,
    )
    assert created_patch.patch_id == PATCH_ID


def test_create_validity_period(
    monkeypatch: pytest.MonkeyPatch,
    client_configuration: Configuration,
    validity_period: ValidityPeriod,
    variable_definition: VariableDefinition,
):
    monkeypatch.setenv(DAPLA_GROUP_CONTEXT, VARDEF_EXAMPLE_ACTIVE_GROUP)
    VardefClient.set_config(client_configuration)
    my_variable = variable_definition
    assert isinstance(
        my_variable.create_validity_period(validity_period),
        CompletePatchOutput,
    )


@pytest.mark.usefixtures("set_temp_workspace")
def test_write_template(tmp_path: Path):
    with patch.object(Path, "cwd", return_value=tmp_path):
        result = Vardef.write_template_to_file()
        assert result.split(".yaml", 1)[1] == " Successfully written to file"


@pytest.mark.usefixtures("_delete_workspace_dir")
def test_write_template_no_workspace(tmp_path: Path):
    with patch.object(Path, "cwd", return_value=tmp_path):
        with pytest.raises(FileNotFoundError) as exc_info:
            Vardef.write_template_to_file()
        assert (
            str(exc_info.value)
            == "'work' directory not found and env WORKSPACE_DIR is not set."
        )


@pytest.mark.usefixtures("_delete_workspace_dir")
def test_write_template_path_no_env_value(tmp_path: Path):
    workspace_dir = tmp_path / "work"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    with patch.object(Path, "cwd", return_value=workspace_dir):
        result = Vardef.write_template_to_file()
    # remove time stamp result
    result_without_timestamp = result.rsplit("_", 1)[0] + ".yaml"
    result_without_timestamp += result.split(".yaml", 1)[1]
    expected_result = f"File path {workspace_dir}/variable_definitions/variable_definition_template.yaml Successfully written to file"
    assert result_without_timestamp == expected_result
