import json

from dapla_metadata.variable_definitions.generated.vardef_client.exceptions import (
    OpenApiException,
)


# validation exception
class VardefClientException(OpenApiException):
    """Class for handling exceptions from Vardef."""

    def __init__(self, message: str, code: str) -> None:
        """Inherit from OpenApiException."""
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self) -> str:
        """Custom message."""
        data = json.loads(self.message)
        error = data["message"]
        embedded = data["_embedded"]
        messages = [error["message"] for error in embedded["errors"]]
        return f"{error}: {messages}"
