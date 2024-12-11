"""Tests for Vardef client exception handling."""

from dapla_metadata.variable_definitions.exceptions import VardefClientException
from tests.utils.constants import BAD_REQUEST_STATUS
from tests.utils.constants import CONSTRAINT_VIOLATION_BODY
from tests.utils.constants import CONSTRAINT_VIOLATION_BODY_MISSING_FIELD
from tests.utils.constants import CONSTRAINT_VIOLATION_BODY_MISSING_MESSAGES
from tests.utils.constants import CONSTRAINT_VIOLATION_BODY_MISSING_VIOLATIONS
from tests.utils.constants import NOT_FOUND_STATUS


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
        str(exc) == "Status 400: ["
        "{'Field': 'updateVariableDefinitionById.updateDraft.owner.team', 'Message': 'Invalid Dapla team'}, "
        "{'Field': 'updateVariableDefinitionById.updateDraft.owner.team', 'Message': 'must not be empty'}]"
    )


def test_constraint_violation_missing_messages():
    response_body = CONSTRAINT_VIOLATION_BODY_MISSING_MESSAGES
    exc = VardefClientException(response_body)
    assert exc.status == BAD_REQUEST_STATUS
    assert exc.detail[0]["Message"] == "No message provided"


def test_constraint_violation_empty_violations():
    response_body = CONSTRAINT_VIOLATION_BODY_MISSING_VIOLATIONS
    exc = VardefClientException(response_body)
    assert exc.status == BAD_REQUEST_STATUS
    assert str(exc) == "Status 400: []"


def test_constraint_violation_empty_field():
    response_body = CONSTRAINT_VIOLATION_BODY_MISSING_FIELD
    exc = VardefClientException(response_body)
    assert exc.status == BAD_REQUEST_STATUS
    assert str(exc) == (
        "Status 400: ["
        "{'Field': 'Unknown field', 'Message': 'Invalid Dapla team'}, "
        "{'Field': 'Unknown field', 'Message': 'must not be empty'}]"
    )
