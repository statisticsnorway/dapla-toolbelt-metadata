import pytest

from dapla_metadata.variable_definitions._client import VardefClient
from dapla_metadata.variable_definitions.generated.vardef_client.configuration import (
    Configuration,
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
from dapla_metadata.variable_definitions.vardef import Vardef
from dapla_metadata.variable_definitions.variable_definition import CompletePatchOutput
from dapla_metadata.variable_definitions.variable_definition import VariableDefinition
from tests.utils.constants import DAPLA_GROUP_CONTEXT
from tests.utils.constants import VARDEF_EXAMPLE_ACTIVE_GROUP
from tests.utils.constants import VARDEF_EXAMPLE_DATE
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID
from tests.variable_definitions.test_vardef import PATCH_ID


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


@pytest.mark.usefixtures("configure_vardef_client", "set_dapla_group_context")
def test_create_patch(
    patch: Patch,
    variable_definition: VariableDefinition,
):
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


def test_str(variable_definition):
    assert (
        str(variable_definition)
        == """{
  "id": "wypvb3wd",
  "patch_id": 1,
  "name": {
    "nb": "test",
    "nn": "test",
    "en": "test"
  },
  "short_name": "var_test",
  "definition": {
    "nb": "test",
    "nn": "test",
    "en": "test"
  },
  "classification_reference": "91",
  "unit_types": [
    "01"
  ],
  "subject_fields": [
    "a",
    "b"
  ],
  "contains_special_categories_of_personal_data": true,
  "variable_status": "PUBLISHED_EXTERNAL",
  "measurement_type": "test",
  "valid_from": "2024-11-01",
  "valid_until": null,
  "external_reference_uri": "http://www.example.com",
  "comment": {
    "nb": "test",
    "nn": "test",
    "en": "test"
  },
  "related_variable_definition_uris": [
    "http://www.example.com"
  ],
  "owner": {
    "team": "my_team",
    "groups": [
      "my_team_developers"
    ]
  },
  "contact": {
    "title": {
      "nb": "test",
      "nn": "test",
      "en": "test"
    },
    "email": "me@example.com"
  },
  "created_at": "2024-11-01T00:00:00",
  "created_by": "ano@ssb.no",
  "last_updated_at": "2024-11-01T00:00:00",
  "last_updated_by": "ano@ssb.no"
}"""
    )
