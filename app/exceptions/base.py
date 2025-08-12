from datetime import datetime, timezone
from typing import Any

from fastapi.responses import JSONResponse
from starlette import status


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
    ):
        super().__init__(message or self.message)

        self.code = code or self.code
        self.http_status_code = http_status_code or self.http_status_code
        self.message = message or self.message

    @classmethod
    def from_base_exception(cls, exception: Exception):
        return cls(
            message=str(exception) or cls.message,
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
