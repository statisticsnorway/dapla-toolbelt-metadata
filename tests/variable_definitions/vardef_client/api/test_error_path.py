"""Simple tests for exceptions."""

import json

import pytest

from dapla_metadata.variable_definitions.exceptions import VardefClientException
from dapla_metadata.variable_definitions.generated import vardef_client
from dapla_metadata.variable_definitions.generated.vardef_client.exceptions import (
    OpenApiException,
)
from tests.utils.constants import BAD_REQUEST_STATUS
from tests.utils.constants import CONSTRAINT_VIOLATION_BODY
from tests.utils.constants import NOT_FOUND_STATUS


def test_not_found_variable(api_client):
    api_instance = vardef_client.VariableDefinitionsApi(api_client)
    with pytest.raises(
        OpenApiException,
        match="Variable with ID invalid id not found",
    ) as exc_info:
        api_instance.get_variable_definition_by_id("invalid id")
    response = exc_info.value.body
    result = json.loads(response)
    assert result["detail"] == "Variable with ID invalid id not found"


def test_not_found_response(api_client):
    api_instance = vardef_client.VariableDefinitionsApi(api_client)
    with pytest.raises(
        OpenApiException,
        match="Variable with ID invalid id not found",
    ) as e:
        api_instance.get_variable_definition_by_id("invalid id")
    exception = VardefClientException(e.value.body)
    assert str(exception) == "Status 404: Variable with ID invalid id not found"


def test_valid_response_body():
    response_body = '{"status": 400, "detail": "Bad Request"}'
    exc = VardefClientException(response_body)
    assert exc.status == BAD_REQUEST_STATUS
    assert exc.detail == "Bad Request"
    assert str(exc) == "Status 400: Bad Request"


def test_invalid_json():
    response_body = "Not a JSON string"
    exc = VardefClientException(response_body)
    assert exc.status == "Unknown"
    assert exc.detail == "Invalid response body"
    assert str(exc) == "Status Unknown: Invalid response body"


def test_missing_keys():
    response_body = '{"status": 404}'
    exc = VardefClientException(response_body)
    assert exc.status == NOT_FOUND_STATUS
    assert exc.detail == "No detail provided"
    assert str(exc) == "Status 404: No detail provided"


def test_constraint_violation():
    response_body = CONSTRAINT_VIOLATION_BODY
    exc = VardefClientException(response_body)
    assert exc.status == BAD_REQUEST_STATUS
    assert exc.detail[0]["Message"] == "Invalid Dapla team"
    assert (
        str(exc)
        == "Status 400: [{'Field': 'updateVariableDefinitionById.updateDraft.owner.team', 'Message': 'Invalid Dapla team'}, {'Field': 'updateVariableDefinitionById.updateDraft.owner.team', 'Message': 'must not be empty'}]"
    )
