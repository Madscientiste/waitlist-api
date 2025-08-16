import uuid

from fastapi.exceptions import RequestValidationError
from fastapi.responses import Response
from pydantic import ValidationError as PydanticValidationError
from starlette.types import ASGIApp, Receive, Scope, Send

from app import logger
from app.context.app import app_context, get_app_context
from app.exceptions.base import BaseAppException
from app.exceptions.basic import InternalError
from app.exceptions.validation import ValidationError


class ContextMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())

        with app_context() as ctx:
            with ctx.http(
                request_id=request_id,
                path=scope.get("path", "unknown"),
                method=scope.get("method", "unknown"),
                # Any other metadata we want to add to the request
            ):
                await self.app(scope, receive, send)


class ExceptionHandlerMiddleware:
    """
    ASGI-level exception handler middleware.

    This middleware catches exceptions at the ASGI layer rather than relying on
    FastAPI's ``app.add_exception_handler``. Unlike the latter, it wraps the entire
    middleware and routing stack, ensuring that exceptions are caught only after
    request context and other middlewares have been applied. This guarantees that
    contextual metadata (e.g., request_id, path, method) is available when logging
    or formatting error responses.

    Note:
        This middleware should be added *last* in the middleware stack so that
        all other middlewares (e.g., context, database session, authentication)
        can set up state before exception handling occurs.

    Args:
        app (ASGIApp): The ASGI application to wrap.
    """

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        try:
            await self.app(scope, receive, send)
        except (RequestValidationError, PydanticValidationError) as exc:
            response = ValidationError(details=exc.errors())
            await response(scope, receive, send)
        except BaseAppException as exc:
            response = exc.to_json_response()
            await response(scope, receive, send)
        except Exception as exc:
            response = BaseAppException.from_base_exception(exc)
            await response(scope, receive, send)
