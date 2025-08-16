from fastapi import status

from app.exceptions.base import BaseAppException


class InvalidReferenceError(BaseAppException):
    """Raised when offer or representation does not exist."""

    code = "INVALID_REFERENCE"
    http_status_code = status.HTTP_404_NOT_FOUND
    message = "Invalid offer or representation reference"


class WaitlistNotAvailableError(BaseAppException):
    """Raised when waitlist is not available (tickets still on sale)."""

    code = "WAITLIST_NOT_AVAILABLE"
    http_status_code = status.HTTP_400_BAD_REQUEST
    message = "Waitlist is not available - tickets are still on sale"


class InvalidQuantityError(BaseAppException):
    """Raised when requested quantity is invalid or exceeds limits."""

    code = "INVALID_QUANTITY"
    http_status_code = status.HTTP_400_BAD_REQUEST
    message = "Invalid quantity specified"


class UserAlreadyOnWaitlistError(BaseAppException):
    """Raised when user tries to join a waitlist they're already on."""

    code = "USER_ALREADY_ON_WAITLIST"
    http_status_code = status.HTTP_409_CONFLICT
    message = "User is already on this waitlist"


class UserNotOnWaitlistError(BaseAppException):
    """Raised when user tries to leave a waitlist they're not on."""

    code = "USER_NOT_ON_WAITLIST"
    http_status_code = status.HTTP_404_NOT_FOUND
    message = "User is not on this waitlist"


class UserDoesNotExistError(BaseAppException):
    """Raised when user does not exist."""

    code = "USER_DOES_NOT_EXIST"
    http_status_code = status.HTTP_404_NOT_FOUND
    message = "User does not exist"
