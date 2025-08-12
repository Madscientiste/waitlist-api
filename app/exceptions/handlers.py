from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from app.exceptions.validation import ValidationError


async def handle_validation_error(_, exc: RequestValidationError | PydanticValidationError) -> JSONResponse:
    """
    Handle validation errors from FastAPI and Pydantic.
    """

    raise ValidationError(
        message="Validation failed",
        details=exc.errors(),
    )
