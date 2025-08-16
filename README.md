# Event Waiting-List API

## 🚀 Tech Stack

- **Python 3.13** - Latest Python features and performance
- **FastAPI 0.116** - Modern, fast web framework
- **SQLAlchemy 2.0** - Advanced ORM with async support
- **Docker** - Containerized deployment
- **Pytest** - Comprehensive testing framework

## 📋 Assumptions

This service is designed to be consumed by other services in a microservices architecture. We provide comprehensive waitlist management capabilities, but expect callers to provide metadata about users, events, and other domain entities.

## 🏃‍♂️ Quick Start

### Prerequisites

Make sure you have Python 3.13+ and [uv](https://docs.astral.sh/uv/) installed.

### Installation & Running

```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Start development server
fastapi dev app/api/app.py
# or alternatively
uvicorn app.api.app:app --reload

# Run tests
uv run pytest -q

# Run with verbose output
uv run pytest -v
```

### 🐳 Docker

```bash
# Build the image
docker build -t waitlist-api .

# Run the container
docker run -p 8000:8000 waitlist-api

# Health check
curl http://localhost:8000/api/ping
```

### 🌐 Access Points

Once running, you can access:

- **API Endpoints**: `http://localhost:8000/api`
- **Interactive Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/api/ping`
- **Swagger UI**: `http://localhost:8000/swagger`

## 🏗️ Architecture Overview

### Core Components

```
app/
├── api/                   # FastAPI application & routes
│   ├── app.py             # Main ASGI app with some configuration
│   ├── routes/            # API endpoint definitions
│   └── schemas/           # Pydantic models
├── database/              # SQLAlchemy setup & helpers
│   ├── connection.py      # Engine, sessions, transactions
│   ├── middleware.py      # Per-request session management
│   └── model.py           # Base model with helpers
├── models/                # Domain models
├── repositories/          # Data access layer
├── exceptions/            # Custom exception hierarchy
└── context/               # Request context management
```

## 🔄 Request Lifecycle

Understanding how requests flow through the system:

### 1. 📥 Incoming Request

- Generate unique `request_id`
- Capture HTTP `method` and `path`

### 2. 🎯 Context Middleware

- Initialize application context with request metadata
- Make context accessible via `get_app_context()` throughout request

### 3. 🗄️ Database Session Middleware

- Open per-request SQLAlchemy session using `db.scope()`
- Auto-cleanup: commit on success, rollback on `SQLAlchemyError`

### 4. 🎪 Route Handler Execution

- Execute your business logic
- Use `transaction()` for commits, `savepoint()` for nested rollbacks
- Inside transactions: `save()`/`delete()` only flush
- Outside transactions: `save()`/`delete()` auto-commit

### 5. ✅ Validation Error Handling

- FastAPI/Pydantic validation errors → normalized responses
- Detailed error information in `error.details`

### 6. 🚨 Exception Handling

- `BaseAppException` → structured error response
- Uncaught exceptions → generic 500 `InternalError`
- All errors logged for monitoring/debugging

#### 📝 Error Envelope

All API errors follow this consistent structure:

```json
{
  "error": {
    "status": "VALIDATION_ERROR",
    "code": 422,
    "message": "Validation failed",
    "details": [
      {
        "loc": ["query", "limit"],
        "msg": "ensure this value is greater than 0",
        "type": "value_error"
      }
    ],
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "method": "GET",
    "path": "/api/offers/123/representations/456/waitlist",
    "timestamp": "2025-01-27T12:00:00Z"
  }
}
```

### Basic Errors Types

> If needed, more errors types are defined at `app/exceptions/*`

| Status Code | Error Type                 | Description             |
| ----------- | -------------------------- | ----------------------- |
| `400`       | `INVALID_ARGUMENT`         | Bad request parameters  |
| `404`       | `NOT_FOUND`                | Resource not found      |
| `409`       | `USER_ALREADY_ON_WAITLIST` | Conflict state          |
| `422`       | `VALIDATION_ERROR`         | Input validation failed |
| `500`       | `INTERNAL`                 | Server error            |

## 🧪 Testing

### Running Tests

```bash
# Quick test run
uv run pytest -q

# Specific test file
uv run pytest tests/api/test_error_responses.py -v

# Test specific pattern
uv run pytest -k "waitlist" -v
```

### Test Structure

```
tests/
├── api/                  # API endpoint tests
├── database/             # Database layer tests
├── repositories/         # Repository tests with real data
└── conftest.py           # Shared test fixtures
```

## 📊 API Endpoints

### Waitlist API

| Method   | Endpoint                                                              | Description           |
| -------- | --------------------------------------------------------------------- | --------------------- |
| `GET`    | `/api/offers/{offer_id}/representations/{repr_id}/waitlist`           | List waitlist entries |
| `GET`    | `/api/offers/{offer_id}/representations/{repr_id}/waitlist/{user_id}` | Get user position     |
| `POST`   | `/api/offers/{offer_id}/representations/{repr_id}/waitlist`           | Join waitlist         |
| `DELETE` | `/api/offers/{offer_id}/representations/{repr_id}/waitlist/{user_id}` | Leave waitlist        |

### System

| Method | Endpoint    | Description  |
| ------ | ----------- | ------------ |
| `GET`  | `/api/ping` | Health check |

## 🚀 CI/CD

This project uses GitHub Actions for continuous integration:

- **Automated Testing**: Runs on every push and PR to main branch
- **Python 3.13**: Tests against the target Python version
- **UV Integration**: Fast dependency installation with uv

### Pipeline Steps

1. **Setup**: Install Python 3.13 and uv package manager
2. **Dependencies**: Install project dependencies with `uv sync`
3. **Testing**: Run all tests with `pytest -v`

## 📖 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
