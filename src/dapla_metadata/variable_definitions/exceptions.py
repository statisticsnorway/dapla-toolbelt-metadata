"""Vardef client exceptions."""

import json
from functools import wraps

from pytz import UnknownTimeZoneError
from yaml import YAMLError

from dapla_metadata.variable_definitions.generated.vardef_client.exceptions import (
    OpenApiException,
)


class VardefClientException(OpenApiException):
    """Custom exception to represent errors encountered in the Vardef client.

    This exception extracts and formats error details from a JSON response body
    provided by the Vardef API, enabling more descriptive error messages.
    If the response body cannot be parsed as JSON or lacks expected keys,
    default values are used to provide meaningful feedback.
    """

    def __init__(self, response_body: str) -> None:
        """Initialize the exception with a JSON-formatted response body.

        Args:
            response_body (str): The JSON string containing error details
                                from the Vardef API response.

        Attributes:
            status (str): The status code from the response, or "Unknown status"
                        if not available or the response is invalid.
            detail (str || list): A detailed error message from the response, or
                        "No detail provided" if not provided. If "Constraint violation"
                        detail contains 'field' and 'message'.
            response_body (str): The raw response body string, stored for
                                debugging purposes.
        """
        try:
            data = json.loads(response_body)
            self.status = data.get("status", "Unknown status")
            if data.get("title") == "Constraint Violation":
                violations = data.get("violations", [])
                self.detail = "".join(
                    f"\n{violation.get('field', 'Unknown field')}: {violation.get('message', 'No message provided')}"
                    for violation in violations
                )

            else:
                self.detail = data.get("detail", "No detail provided")
            self.response_body = response_body
        except (json.JSONDecodeError, TypeError):
            self.status = "Unknown"
            self.detail = "Could not decode error response from API"
            data = None
        super().__init__(f"Status {self.status}: {self.detail}")


def vardef_exception_handler(method):  # noqa: ANN201, ANN001
    """Decorator for handling exceptions in Vardef."""

    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):  # noqa: ANN001, ANN002, ANN003
        try:
            return method(self, *method_args, **method_kwargs)
        except OpenApiException as e:
            raise VardefClientException(e.body) from e

    return _impl


class VardefTemplateError(Exception):
    """Custom exception for handling errors related to YAML template generation."""

    def __init__(self, message: str, *args) -> None:  # noqa: ANN002
        """Accepting the message and any additional arguments."""
        super().__init__(message, *args)
        self.message = message
        self.args = args

    def __str__(self) -> str:
        """Returning a custom string representation of the exception."""
        return f"VardefTemplateException: {self.message}"


def template_generator_handler(method):  # noqa: ANN201, ANN001
    """Decorator for handling exceptions when generating yaml files."""
    wraps(method)

    def _impl(self, *method_args, **method_kwargs):  # noqa: ANN001, ANN002, ANN003
        try:
            return method(
                self,
                *method_args,
                **method_kwargs,
            )
        except FileNotFoundError as e:
            # Catch FileNotFoundError and raise a custom exception with specific message
            msg = (
                f"File not found: {method_kwargs.get('file_path', 'unknown file path')}"
            )
            raise VardefTemplateError(msg) from e
        except FileExistsError as e:
            # Catch FileNotFoundError and raise a custom exception with specific message
            msg = f"File already exists and can not be saved: {method_kwargs.get('file_path', 'unknown file path')}"
            raise VardefTemplateError(msg) from e
        except PermissionError as e:
            # Catch PermissionError and raise a custom exception with specific message
            msg = f"Permission denied when accessing the file: {method_kwargs.get('file_path', 'unknown')}"
            raise VardefTemplateError(msg) from e
        except UnknownTimeZoneError as e:
            # Catch PermissionError and raise a custom exception with specific message
            msg = f"Timezone is unknown: {method_kwargs.get('time_zone', 'unknown')}"
            raise VardefTemplateError(msg) from e
        except YAMLError as e:
            # Catch PermissionError and raise a custom exception with specific message
            msg = "Not possible to serialize yaml"
            raise VardefTemplateError(msg) from e

    return _impl
