from typing import Any

import httpx
from pydantic import ValidationError


class PillarError(Exception):
    """Base exception class for Pillar SDK errors."""

    pass


class PillarAPIError(PillarError):
    """Exception raised when the Pillar API returns an error response."""

    def __init__(self, status_code: int, response_text: str):
        self.status_code = status_code
        self.response_text = response_text
        super().__init__(f"Pillar API error (status {status_code}): {response_text}")


class PillarValidationError(PillarError):
    """Exception raised when a Pillar validation fails."""

    def __init__(self, validation_error: ValidationError):
        self.validation_error = validation_error
        super().__init__(str(validation_error))

    def errors(self):
        """Get the validation errors."""
        return self.validation_error.errors()


class PillarTimeoutError(PillarError, httpx.TimeoutException):
    """Exception raised when the Pillar API times out."""

    pass


class PillarRequestError(PillarError, httpx.RequestError):
    """Exception raised when there is a connection error with Pillar API."""

    pass


class PillarBlockError(PillarError):
    """Exception raised when a block is detected."""

    def __init__(self, request: Any, response: Any):
        # Use Any to avoid issues with TypeVar constraints
        self.request = request
        self.response = response
        super().__init__()
