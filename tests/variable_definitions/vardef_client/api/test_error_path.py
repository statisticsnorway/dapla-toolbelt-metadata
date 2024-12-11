"""Simple tests for exceptions."""

import json

import pytest

from dapla_metadata.variable_definitions.exceptions import VardefClientException
from dapla_metadata.variable_definitions.generated import vardef_client
from dapla_metadata.variable_definitions.generated.vardef_client.exceptions import (
    OpenApiException,
)


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
