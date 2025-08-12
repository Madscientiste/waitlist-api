from fastapi import status

from app.exceptions.base import BaseAppException


class BadRequest(BaseAppException):
    code = "INVALID_ARGUMENT"
    http_status_code = status.HTTP_400_BAD_REQUEST
    message = "Bad request"


class NotFound(BaseAppException):
    code = "NOT_FOUND"
    http_status_code = status.HTTP_404_NOT_FOUND
    message = "Resource not found"


class InternalError(BaseAppException):
    code = "INTERNAL"
    http_status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Internal Server Error"
