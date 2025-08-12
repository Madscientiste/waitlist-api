from sqlalchemy.exc import SQLAlchemyError
from starlette.types import ASGIApp, Receive, Scope, Send

from .connection import db


class DatabaseSessionMiddleware:
    """Middleware for managing database sessions within a request scope.

    This middleware automaticalladd_to_classy creates a database session using the provided
    `Database` instance within the scope of each request. It also handles session
    commit or rollback based on the `commit_on_exit` flag and closes the session
    after the request completes.

    Args:
      app: The ASGI application instance.
      database: An instance of the `Database` class for managing database connections.
    """

    def __init__(self, app: ASGIApp):
        self.app = app
        self.database = db

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        with db.scope():
            try:
                await self.app(scope, receive, send)
            except SQLAlchemyError as e:
                db.session.rollback()
                raise e from e
            finally:
                db.session.close()
