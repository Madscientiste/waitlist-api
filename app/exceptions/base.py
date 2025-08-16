from datetime import datetime, timezone
from typing import Any

from fastapi.responses import JSONResponse, Response
from starlette import status
from starlette.types import Receive, Scope, Send

from app import logger


class BaseAppException(Exception):
    code: str = "INTERNAL_APP_ERROR"
    http_status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    message: str = "An unexpected error occurred"

    # Optional enrichments for the response envelope
    details: list[Any] | None = None

    def __init__(
        self,
        code: str | None = None,
        http_status_code: int | None = None,
        message: str | None = None,
        details: list[Any] | None = None,
    ):
        super().__init__(message or self.message)
        self.code = code or self.code
        self.http_status_code = http_status_code or self.http_status_code
        self.message = message or self.message
        self.details = details

    def __call__(self, scope: Scope, receive: Receive, send: Send):
        """Allow the exception to be used directly as an ASGI response."""
        # This log each time an exception is raised but rendered to the user
        # This can be any exception, not just the ones we raise
        logger.exception(self)
        return self.to_json_response()(scope, receive, send)

    @classmethod
    def from_base_exception(cls, exception: Exception):
        return cls(
            message="Internal Server Error",
            http_status_code=cls.http_status_code,
            code=cls.code,
        )

    def to_json_response(self) -> JSONResponse:
        from app.context.app import get_app_context  # local import to avoid cycles

        ctx = get_app_context()

        return JSONResponse(
            status_code=self.http_status_code,
            content={
                "error": {
                    "status": self.code,
                    "code": self.http_status_code,
                    "message": self.message,
                    #
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "request_id": ctx.http.get("request_id"),
                    "method": ctx.http.get("method"),
                    "path": ctx.http.get("path"),
                    # useful for the validation errors, where the frontend can consume these.
                    "details": self.details or None,
                }
            },
        )
