"""Simple tests for exceptions."""

import json

import pytest

from dapla_metadata.variable_definitions.generated import vardef_client
from dapla_metadata.variable_definitions.generated.vardef_client.exceptions import (
    BadRequestException,
)
from dapla_metadata.variable_definitions.generated.vardef_client.exceptions import (
    OpenApiException,
)
from tests.utils.constants import VARDEF_EXAMPLE_ACTIVE_GROUP
from tests.utils.constants import VARDEF_EXAMPLE_DEFINITION_ID


def test_create_draft(api_client, draft_invalid_unit_types):
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    with pytest.raises(BadRequestException):
        api_instance.create_variable_definition(
            VARDEF_EXAMPLE_ACTIVE_GROUP,
            draft_invalid_unit_types,
        )


def test_error_message_create_draft(api_client, draft_invalid_unit_types):
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    try:
        api_instance.create_variable_definition(
            VARDEF_EXAMPLE_ACTIVE_GROUP,
            draft_invalid_unit_types,
        )
    except BadRequestException as e:
        response = e.body
        data = json.loads(response)
        embedded = data["_embedded"]
        message = embedded["errors"]
        last = message[0]["message"]

        assert (
            last
            == "draft.unitTypes[0]: Code a is not a member of classification with id 702"
        )


def test_none_existing_patch(api_client):
    api_instance = vardef_client.PatchesApi(api_client)
    with pytest.raises(OpenApiException):
        api_instance.get_patch(VARDEF_EXAMPLE_DEFINITION_ID, 200)


def test_none_existing_patch_message(api_client):
    api_instance = vardef_client.PatchesApi(api_client)
    try:
        api_instance.get_patch(VARDEF_EXAMPLE_DEFINITION_ID, 200)
    except OpenApiException as e:
        assert (
            str(e.body)
            == "The response /patch-id=200/variable-definition-id=wypvb3wd does not exist!"
        )
