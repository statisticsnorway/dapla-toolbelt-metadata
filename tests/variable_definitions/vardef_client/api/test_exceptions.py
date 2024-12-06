"""Simple tests for exceptions."""

from datetime import date

import pytest

from dapla_metadata.variable_definitions.generated import vardef_client
from dapla_metadata.variable_definitions.generated.vardef_client.exceptions import (
    OpenApiException,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models import (
    language_string_type,
)
from dapla_metadata.variable_definitions.generated.vardef_client.models.draft import (
    Draft,
)
from dapla_metadata.variable_definitions.vardef.exceptions import VardefClientException
from dapla_metadata.variable_definitions.vardef.vardef import Vardef
from tests.utils.constants import VARDEF_EXAMPLE_ACTIVE_GROUP

draft_unittypes = Draft(
    name=language_string_type.LanguageStringType(
        nb=None,
        nn=None,
        en=None,
    ),
    short_name="test",
    definition=language_string_type.LanguageStringType(
        nb=None,
        nn=None,
        en=None,
    ),
    classification_reference="91",
    unit_types=["a"],
    subject_fields=["al"],
    contains_sensitive_personal_information=True,
    measurement_type="01",
    valid_from=date(2024, 11, 1),
    external_reference_uri="http://www.example.com",
    comment=None,
    related_variable_definition_uris=["http://www.example.com"],
    contact=None,
)


def test_create_draft():
    # api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    with pytest.raises(VardefClientException):
        Vardef.create_draft(draft_unittypes)


def test_create_draft_2(api_client):
    api_instance = vardef_client.DraftVariableDefinitionsApi(api_client)
    with pytest.raises(OpenApiException):
        api_instance.create_variable_definition(
            VARDEF_EXAMPLE_ACTIVE_GROUP,
            draft_unittypes,
        )
