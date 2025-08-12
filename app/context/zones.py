from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Literal,
    Optional,
    TypedDict,
    TypeVar,
)

if TYPE_CHECKING:
    from app.context.app import AppContext

# Generic type for zones
T = TypeVar("T", bound=TypedDict)


class HttpZoneData(TypedDict):
    path: str
    method: str
    request_id: str


class CliZoneData(TypedDict):
    command: str


class DatabaseZoneData(TypedDict):
    pass


# Key unions for zones
HttpZoneKey = Literal["path", "method", "request_id"]
CliZoneKey = Literal["command"]


class BaseZone(Generic[T]):
    def __init__(self, app_context: "AppContext", attr_name: str):
        self.app_context = app_context
        self.attr_name = attr_name
        self.kwargs: Dict[str, Any] = {}
        self._prev: Optional[Dict[str, Any]] = None

    def __call__(self, **kwargs):
        self.kwargs = kwargs
        return self

    def __enter__(self):
        current = getattr(self.app_context, self.attr_name)
        if current is not None:
            raise RuntimeError(f"{self.__class__.__name__} already set; nesting is not allowed")
        # Save previous (for future flexibility) even if we forbid nesting now
        # I plan to add support for SOME nested zones, but not all.
        # Eg, maybe having a UserZone ?? idk
        self._prev = current
        setattr(self.app_context, self.attr_name, self.kwargs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clear the zone data on exit
        setattr(self.app_context, self.attr_name, self._prev)

    # Mapping-like access to the current zone data
    def _data(self) -> Optional[Dict[str, Any]]:
        return getattr(self.app_context, self.attr_name)

    def __getitem__(self, key: str) -> Any:
        data = self._data() or {}
        return data[key]

    def get(self, key: str, default: Any = None) -> Any:
        data = self._data() or {}
        return data.get(key, default)

    def __contains__(self, key: str) -> bool:
        data = self._data() or {}
        return key in data


class HttpZone(BaseZone[HttpZoneData]):
    def __call__(self, *, path: str, method: str, request_id: str) -> "HttpZone":
        return super().__call__(path=path, method=method, request_id=request_id)

    def __getitem__(self, key: HttpZoneKey) -> str:
        return super().__getitem__(key)

    def get(self, key: HttpZoneKey, default: Optional[str] = None) -> Any:
        return super().get(key, default)


class CliZone(BaseZone[CliZoneData]):
    def __call__(self, *, command: str) -> "CliZone":
        return super().__call__(command=command)

    def __getitem__(self, key: CliZoneKey) -> str:
        return super().__getitem__(key)

    def get(self, key: CliZoneKey, default: Optional[str] = None) -> Optional[str]:
        return super().get(key, default)


class DatabaseZone(BaseZone[DatabaseZoneData]):
    """
    Database zone placeholder - not implemented due to time constraints.

    Current: Database class manages sessions independently

    Possible use cases?:
    - Distributed tracing: Track database operations across service boundaries
    - Performance monitoring: Store query execution times, slow query alerts
    - Audit logging: Track which user/request performed which database operations
    - Connection pooling metrics: Monitor connection usage and performance
    -"""
