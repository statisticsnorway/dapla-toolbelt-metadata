import functools
from collections.abc import Callable
from http import HTTPStatus
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest
import urllib3

from dapla_metadata._shared.config import DAPLA_GROUP_CONTEXT
from dapla_metadata.variable_definitions._generated.vardef_client.api.variable_definitions_api import (
    VariableDefinitionsApi,
)
from dapla_metadata.variable_definitions._generated.vardef_client.api_client import (
    ApiClient,
)
from dapla_metadata.variable_definitions._generated.vardef_client.configuration import (
    Configuration,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.draft import (
    Draft,
)
from dapla_metadata.variable_definitions._generated.vardef_client.models.variable_status import (
    VariableStatus,
)
from dapla_metadata.variable_definitions._utils._client import VardefClient
from dapla_metadata.variable_definitions.exceptions import STATUS_EXPLANATIONS
from dapla_metadata.variable_definitions.exceptions import VardefClientError
from dapla_metadata.variable_definitions.exceptions import VariableNotFoundError
from dapla_metadata.variable_definitions.vardef import Vardef
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition
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
        VariableDefinition,
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
    with (
        patch.object(
            VariableDefinitionsApi,
            "list_variable_definitions",
            return_value=mock_response,
        ),
        pytest.raises(
            VariableNotFoundError,
            match=f"Variable with short name {short_name} not found",
        ),
    ):
        Vardef.get_variable_definition_by_shortname(short_name=short_name)


def test_get_variable_definition_multiple_variables_returned(
    client_configuration: Configuration,
):
    VardefClient.set_config(client_configuration)
    short_name = "multiple"
    mock_response = ["variable", "variable"]
    with (
        patch.object(
            VariableDefinitionsApi,
            "list_variable_definitions",
            return_value=mock_response,
        ),
        pytest.raises(
            VariableNotFoundError,
            match=f"Lookup by short name {short_name} found multiple variables which should not be possible",
        ),
    ):
        Vardef.get_variable_definition_by_shortname(short_name=short_name)


@patch.object(
    ApiClient,
    "call_api",
)
@pytest.mark.parametrize(
    ("exception"),
    [
        urllib3.exceptions.ProtocolError(),
        urllib3.exceptions.MaxRetryError(
            pool=urllib3.connectionpool.HTTPConnectionPool(host="example.com"),
            url="http://www.example.com",
        ),
    ],
)
def test_urllib_exceptions(
    mock_call_api: Mock,
    exception: urllib3.exceptions.HTTPError,
):
    mock_call_api.side_effect = exception
    with pytest.raises(VardefClientError):
        Vardef.get_variable_definition_by_id(VARDEF_EXAMPLE_DEFINITION_ID)


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
    with pytest.raises(VardefClientError) as e:
        method()
    assert e.value.status == HTTPStatus.NOT_FOUND
    assert str(e.value) == (
        STATUS_EXPLANATIONS[HTTPStatus.NOT_FOUND] + "\nDetail: Not found"
    )


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
    assert isinstance(my_draft, VariableDefinition)
    assert my_draft.id is not None
    assert my_draft.patch_id == 1
    assert my_draft.variable_status == VariableStatus.DRAFT


@pytest.mark.usefixtures("work_folder_complete_patch_output")
def test_create_draft_from_file():
    my_draft = Vardef.create_draft_from_file()
    assert isinstance(my_draft, VariableDefinition)
    assert my_draft.id is not None
    assert my_draft.patch_id == 1
    assert my_draft.variable_status == VariableStatus.DRAFT


def test_create_draft_from_file_specify_path(work_folder_complete_patch_output: Path):
    my_draft = Vardef.create_draft_from_file(work_folder_complete_patch_output)
    assert isinstance(my_draft, VariableDefinition)
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
    assert isinstance(my_draft, VariableDefinition)
    assert my_draft.id is not None
    assert my_draft.patch_id == 1
    assert my_draft.variable_status == VariableStatus.DRAFT
