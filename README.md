# Waiting List API

Event waiting list backend with explicit context, per-request DB sessions, and a unified error envelope.

## Project Stack

- Python 3.13
- FastAPI 0.116
- SQLAlchemy 2.0
- Docker

## Run

```sh
# Install
uv sync

# Ensure your env is active
source .venv/bin/activate

# Dev server
fastapi dev app/api/app.py
# or
uvicorn app.api.app:app --reload

# Tests
uv run pytest -q
```

## Architecture at a glance

- Application / API: `app/api/app.py`, `app/api/routes/*`
- Database/SQLAlchemy setup: `app/database/connection.py`, `app/database/middleware.py`, `app/database/model.py` (engine, scoped session, transactions, base model helpers)

## Middleware execution flow (step-by-step)

1. Incoming HTTP request

- A `request_id` is generated.
- Method and path are captured.

2. ContextMiddleware

- Sets the application context HTTP zone with `request_id`, `method`, `path`.
- The context is accessible anywhere via `get_app_context()` during the request.

3. DatabaseSessionMiddleware

- Opens a per-request SQLAlchemy session using `db.scope()`; binds it to the current scope.
- On successful completion, the session is closed.
- On `SQLAlchemyError`, the session is rolled back, then closed.

4. Route handler

- Executes your endpoint logic.
- Transactions: use `transaction()` for outermost-commit semantics and `savepoint()` for nested rollbacks.
  - Inside `transaction()`: `save()`/`delete()` perform `flush()` only; commit is handled by `transaction()`.
  - Outside transactions: `save()`/`delete()` perform an immediate `commit()`.

5. Validation errors

- `fastapi.exceptions.RequestValidationError` and `pydantic.ValidationError` are normalized by `handle_validation_error` into a 422 envelope (`UnprocessableEntity`).
- `error.details` follows FastAPI/Pydantic `errors()` shape.

6. Application and uncaught errors

- `BaseAppException` is returned as-is in the standard envelope.
- Any other uncaught exception is converted to `InternalError` (500) in the same envelope.
- The global exception middleware logs request metadata and the last exception for monitoring systems (if logging/monitors are configured).

## Error envelope (standardized)

```json
{
  "error": {
    "status": "INTERNAL",
    "code": 500,
    "message": "Internal Server Error",
    "details": [],
    "request_id": "<uuid>",
    "method": "GET",
    "path": "/api/v1/resource",
    "timestamp": "2025-01-01T12:00:00Z"
  }
}
```

## App entry point

- Primary ASGI application: `app/api/app.py` exposes `app: FastAPI`.

### Programmatic usage (scripts/workers)

When running code outside the web server, ensure configuration is loaded, the app context is set, and a DB scope is opened.

```python
from app.config import app_config  # ensures settings are loaded
from app.context.app import app_context
from app.database.connection import db

# Example if having a custom script or CLI env
with app_context() as ctx:
    with ctx.cli(command="bootstrap", ...other_relevant_args):
        with db.scope():
            # Your code here (ORM, services, etc.)
            ...
```

### Transactions (optional)

```python
from app.context.app import app_context
from app.database.connection import db, transaction, savepoint

with app_context() as ctx, db.scope():
    with transaction():
        # writes...
        with savepoint():
            # partial writes...
            ...
```
