from typing import Any

from fastapi import status

from app.exceptions.base import BaseAppException


class ValidationError(BaseAppException):
    code = "VALIDATION_ERROR"
    http_status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    message = "Validation error"

    def __init__(self, message: str = "Validation error", details: list[Any] = None):
        super().__init__(message=message)

        self.details = details
