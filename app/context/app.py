from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional

from app.context.zones import (
    CliZone,
    CliZoneData,
    DatabaseZoneData,
    HttpZone,
    HttpZoneData,
)

# Single context variable for the entire app
_app_context: ContextVar[Optional["AppContext"]] = ContextVar("app_context", default=None)


class AppContext:
    def __init__(self):
        self._http: Optional[HttpZoneData] = None
        self._cli: Optional[CliZoneData] = None
        self._database: Optional[DatabaseZoneData] = None

    @property
    def http(self) -> "HttpZone":
        return HttpZone(self, "_http")

    @property
    def cli(self) -> "CliZone":
        return CliZone(self, "_cli")


@contextmanager
def app_context():
    """Simple context manager for app context"""
    if _app_context.get() is not None:
        raise RuntimeError("App context already set; nesting is not allowed")

    ctx = AppContext()
    token = _app_context.set(ctx)

    try:
        yield ctx
    finally:
        _app_context.reset(token)


def get_app_context() -> AppContext:
    """Get current app context"""
    ctx = _app_context.get()

    if ctx is None:
        raise RuntimeError("App context not set. Use 'with app_context():'")

    return ctx
