"""Simple tests for basic coverage of the generated client."""

from http import HTTPStatus

from tests.utils.constants import VARDEF_EXAMPLE_ACTIVE_GROUP
from tests.utils.constants import VARDEF_EXAMPLE_DATE
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID

from dapla_metadata.variable_definitions.generated import vardef_client


def test_create_draft(api_client, draft):
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    response = api_instance.create_variable_definition_with_http_info(
        VARDEF_EXAMPLE_ACTIVE_GROUP,
        draft,
    )
    assert response.status_code == HTTPStatus.CREATED


def test_update_draft(api_client, update_draft):
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    response = api_instance.update_variable_definition_by_id_with_http_info(
        VARDEF_EXAMPLE_DEFINITION_ID,
        VARDEF_EXAMPLE_ACTIVE_GROUP,
        update_draft,
    )
    assert response.status_code == HTTPStatus.OK


def test_delete_draft(api_client):
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    response = api_instance.delete_variable_definition_by_id_with_http_info(
        VARDEF_EXAMPLE_DEFINITION_ID,
        VARDEF_EXAMPLE_ACTIVE_GROUP,
    )
    assert response.status_code == HTTPStatus.NO_CONTENT


def test_list_variable_definitions(api_client):
    api_instance = vardef_client.VariableDefinitionsApi(api_client)
    response = api_instance.list_variable_definitions_with_http_info()
    assert response.status_code == HTTPStatus.OK


def test_get_variable_definition(api_client):
    api_instance = vardef_client.VariableDefinitionsApi(api_client)
    response = api_instance.get_variable_definition_by_id_with_http_info(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
        date_of_validity=VARDEF_EXAMPLE_DATE,
    )
    assert response.status_code == HTTPStatus.OK


def test_list_validity_periods(api_client):
    api_instance = vardef_client.ValidityPeriodsApi(api_client)
    response = api_instance.list_validity_periods_with_http_info(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert response.status_code == HTTPStatus.OK


def test_create_validity_period(api_client, validity_period):
    api_instance = vardef_client.ValidityPeriodsApi(api_client)
    response = api_instance.create_validity_period_with_http_info(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
        active_group=VARDEF_EXAMPLE_ACTIVE_GROUP,
        validity_period=validity_period,
    )
    assert response.status_code == HTTPStatus.CREATED


def test_list_patches(api_client):
    api_instance = vardef_client.PatchesApi(api_client)
    response = api_instance.get_all_patches_with_http_info(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
    )
    assert response.status_code == HTTPStatus.OK


def test_get_patch(api_client):
    api_instance = vardef_client.PatchesApi(api_client)
    response = api_instance.get_one_patch_with_http_info(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
        patch_id=1,
    )
    assert response.status_code == HTTPStatus.OK


def test_create_patch(api_client, patch):
    api_instance = vardef_client.PatchesApi(api_client)
    response = api_instance.create_patch_with_http_info(
        variable_definition_id=VARDEF_EXAMPLE_DEFINITION_ID,
        active_group=VARDEF_EXAMPLE_ACTIVE_GROUP,
        valid_from=VARDEF_EXAMPLE_DATE,
        patch=patch,
    )
    assert response.status_code == HTTPStatus.CREATED
