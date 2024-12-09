"""Simple tests for exceptions."""

import json

import pytest

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
