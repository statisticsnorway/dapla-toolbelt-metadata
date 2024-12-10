"""Vardef client exceptions."""

import json

from dapla_metadata.variable_definitions.generated.vardef_client.exceptions import (
    OpenApiException,
)


class VardefClientException(OpenApiException):
    """Shape error messages for Vardef client users."""

    def __init__(self, response_body: str) -> None:
        """Initilize response and output formatted error message."""
        data = json.loads(response_body)
        self.status = data["status"]
        self.detail = data["detail"]
        self.response_body = response_body  # Save the full response for debugging
        super().__init__(f"Status {self.status}: {self.detail}")
