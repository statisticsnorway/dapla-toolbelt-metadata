"""Simple tests for exceptions."""

import pytest

from dapla_metadata.variable_definitions.generated import vardef_client
from dapla_metadata.variable_definitions.generated.vardef_client.exceptions import (
    BadRequestException,
)
from tests.utils.constants import VARDEF_EXAMPLE_ACTIVE_GROUP


def test_create_draft(api_client, draft_invalid_unit_types):
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    with pytest.raises(BadRequestException):
        api_instance.create_variable_definition(
            VARDEF_EXAMPLE_ACTIVE_GROUP,
            draft_invalid_unit_types,
        )
