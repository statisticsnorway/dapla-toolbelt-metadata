"""Simple tests for basic coverage of the generated client."""

from http import HTTPStatus

from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID
from tests.utils.microcks_testcontainer import MicrocksContainer

from dapla_metadata.variable_definitions.generated import vardef_client


def test_create_draft(api_client, draft, vardef_mock_service: MicrocksContainer):
    api_client.configuration.host = vardef_mock_service.get_mock_url()
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    active_group = "dapla-felles-developers"
    response = api_instance.create_variable_definition_with_http_info(
        active_group,
        draft,
    )
    assert response.status_code == HTTPStatus.CREATED


def test_update_draft(api_client, update_draft, vardef_mock_service: MicrocksContainer):
    api_client.configuration.host = vardef_mock_service.get_mock_url()
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    active_group = "dapla-felles-developers"
    response = api_instance.update_variable_definition_by_id_with_http_info(
        VARDEF_EXAMPLE_DEFINITION_ID,
        active_group,
        update_draft,
    )
    assert response.status_code == HTTPStatus.OK
