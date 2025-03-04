import pytest

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
from tests.utils.constants import VARDEF_EXAMPLE_DATE
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID
from tests.variable_definitions.test_vardef import PATCH_ID


def test_list_patches():
    landbak = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.list_patches()[0], CompletePatchOutput)


@pytest.mark.usefixtures("_configure_vardef_client", "_set_dapla_group_context")
def test_get_patch():
    landbak = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.get_patch(1), CompletePatchOutput)


@pytest.mark.usefixtures("_configure_vardef_client", "_set_dapla_group_context")
def test_list_validity_periods():
    landbak = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(landbak.list_validity_periods()[0], CompletePatchOutput)


@pytest.mark.usefixtures("_configure_vardef_client", "_set_dapla_group_context")
def test_update_draft(
    update_draft: UpdateDraft,
):
    my_draft = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(my_draft.update_draft(update_draft), CompletePatchOutput)


@pytest.mark.usefixtures("_configure_vardef_client", "_set_dapla_group_context")
def test_delete_draft():
    my_draft = Vardef.get_variable_definition_by_id(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert my_draft.id is not None
    result = my_draft.delete_draft()
    assert result == f"Variable {VARDEF_EXAMPLE_DEFINITION_ID} safely deleted"


@pytest.mark.usefixtures("_configure_vardef_client", "_set_dapla_group_context")
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


@pytest.mark.usefixtures("_configure_vardef_client", "_set_dapla_group_context")
def test_create_validity_period(
    validity_period: ValidityPeriod,
    variable_definition: VariableDefinition,
):
    my_variable = variable_definition
    assert isinstance(
        my_variable.create_validity_period(validity_period),
        CompletePatchOutput,
    )


@pytest.mark.usefixtures(
    "_configure_vardef_client",
    "_set_dapla_group_context",
    "set_temp_workspace",
)
def test_update_draft_from_file():
    my_draft = Vardef.write_variable_to_file(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert isinstance(my_draft.update_draft_from_file(), CompletePatchOutput)


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
