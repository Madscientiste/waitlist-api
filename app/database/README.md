# Database Module

This module provides a robust database abstraction layer built on SQLAlchemy with automatic session management, transaction handling, and request-scoped database operations.

## Architecture Overview

The database module is designed around three core principles:

1. **Automatic Session Management** - Sessions are automatically created and cleaned up per request
2. **Transaction Safety** - Built-in transaction handling with automatic rollback on errors
3. **Context-Aware Operations** - Database operations automatically adapt to their execution context

## Core Components

### 1. Connection Management (`connection.py`)

#### `Database` Class

The main database connection manager that handles:

- Engine creation and configuration
- Session factory management
- Request-scoped session isolation

#### Key Methods:

- **`scope()`** - Context manager for request-scoped database operations
- **`session`** - Property that returns the current session for the active scope

#### Global Transaction Functions:

- **`transaction()`** - Context manager for database transactions
- **`savepoint()`** - Create nested savepoints within transactions
- **`is_in_transaction()`** - Check if currently in a transaction block

### 2. Base Model (`model.py`)

#### `BaseModel` Class

Abstract base class for all database models with:

- Automatic timestamp management (`created`, `updated`)
- Built-in session access via `self.session`
- Transaction awareness via `self.is_in_transaction`
- Convenient `save()` and `delete()` methods

#### Key Features:

- **Automatic Timestamps**: `created` and `updated` fields are automatically managed
- **Smart Transaction Handling**: Models automatically flush or commit based on context
- **Session Integration**: Models have direct access to the current session

### 3. Middleware (`middleware.py`)

#### `DatabaseSessionMiddleware`

ASGI middleware that:

- Automatically creates database sessions for each HTTP request
- Handles session cleanup and error rollback
- Integrates with the request lifecycle

## Usage Patterns

### Basic Model Operations

```python
from app.models import Event

# Create and save
event = Event(
    id="ev_001",
    title="Jazz Festival 2025",
    description="Annual jazz festival"
)
event.save()  # Automatically commits if not in transaction

# Query
events = Event.session.query(Event).all()

# Update
event.title = "Updated Title"
event.save()

# Delete
event.delete()
```

### Transaction Management

```python
from app.database.connection import transaction

# Simple transaction
with transaction():
    event1 = Event(id="ev_001", title="Event 1").save()
    event2 = Event(id="ev_002", title="Event 2").save()
    # Both are committed together, or rolled back if any fails

# Nested transactions with savepoints
with transaction():
    event1 = Event(id="ev_001", title="Event 1").save()

    with savepoint():
        event2 = Event(id="ev_002", title="Event 2").save()
        # This can be rolled back independently
```

### Request-Scoped Operations

```python
from app.database.connection import db

# In FastAPI route handlers, sessions are automatically managed
@app.get("/events")
async def get_events():
    # Session is automatically created and cleaned up
    events = Event.session.query(Event).all()
    return events

# Manual scope management
with db.scope():
    event = Event.session.query(Event).first()
    # Session is isolated and automatically cleaned up
```

## Session Lifecycle

1. **Request Start**: Middleware creates a new session via `db.scope()`
2. **Request Processing**: All database operations use the same session
3. **Request End**: Session is automatically closed and cleaned up
4. **Error Handling**: Automatic rollback on SQLAlchemy errors

## Transaction Behavior

### Inside Transactions

- Models automatically `flush()` changes
- Outer transaction handles commit/rollback
- Changes are visible within the same transaction

### Outside Transactions

- Models automatically `commit()` changes immediately
- Each operation is atomic
- Changes are immediately visible

## Configuration

Database configuration is handled via `app.config.app_config`:

- **Environment**: `testing`, `local`, `dev`, `prod`
- **Database Type**: Automatically switches to SQLite for testing/local
- **Connection Pool**: Configurable pool size and settings
- **Timezone**: Defaults to Europe/Paris

## Testing

The database module is designed for easy testing:

- **SQLite**: Automatically used in testing environment
- **Session Isolation**: Each test gets a clean session
- **Transaction Rollback**: Tests can use transactions without affecting other tests

```python
def test_event_creation(session):
    event = Event(id="test_001", title="Test Event").save()
    assert event.id == "test_001"
    # Session is automatically cleaned up after test
```

## Best Practices

1. **Use `self.session`** in models instead of importing session
2. **Wrap related operations** in transactions for atomicity
3. **Let the framework handle** session lifecycle
4. **Use savepoints** for complex nested operations
5. **Avoid manual session management** unless absolutely necessary

## Error Handling

The module provides automatic error handling:

- **SQLAlchemy Errors**: Automatically trigger rollback
- **Transaction Failures**: Automatic cleanup and rollback
- **Session Errors**: Automatic session cleanup and recreation

## Performance Considerations

- **Session Reuse**: Sessions are reused within request scope
- **Automatic Cleanup**: Prevents session leaks and memory issues
