import uuid

from starlette.types import ASGIApp, Receive, Scope, Send

from app.context.app import app_context


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
