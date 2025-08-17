# Event Waiting-List API

## 🚀 Tech Stack

- **Python 3.13** - Latest Python features and performance
- **FastAPI 0.116** - Modern, fast web framework
- **SQLAlchemy 2.0** - Advanced ORM with async support
- **Docker** - Containerized deployment
- **Pytest** - Comprehensive testing framework
- **Sqlite or Postgres** - both are supported, but sqlite is used for simplicity. in production, postgres would be preferred.

## Things i considered

- This service is designed to be consumed by other services in a microservices architecture.
- the waitlist is a FIFO queue, so the first user to join the waitlist is the first to be "notified" when tickets are available.
- Waitlist sizes are expected to be manageable (hundreds to low thousands of entries per offer/representation).
- Position gaps after users leave are acceptable for simplicity (no automatic reordering).
- ... thats all i can think of for now.

## 🏃‍♂️ Quick Start

### Prerequisites

Make sure you have Python 3.13+ and [uv](https://docs.astral.sh/uv/) installed.

### Installation & Running

> Note: Don't forget to set the environment variables in the `.env` from the `.env.example` file.

### 🐳 Docker ( fastest )

```bash
# Build the image
docker compose up api --build

# Health check
curl http://localhost:8000/api/ping
```

### 🐍 Locally

```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Initialize the database with the data/*.csv files
python -m app.bootstrap

# Start development server
fastapi dev app/api/app.py
# or alternatively
uvicorn app.api.app:app --reload

# Run tests
uv run pytest -q

# Run with verbose output
uv run pytest -v
```

### Access Points

Once running, you can access:

- **API Endpoints**: [http://localhost:8000/api](http://localhost:8000/api)
- **Health Check**: [http://localhost:8000/api/ping](http://localhost:8000/api/ping)
- **OpenAPI UI**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Architecture Overview

### Files structure

> Note: Somtimes i like to add Readmees to some directores to fuirther explain their purpose. This is the case with `database/`.

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
└── context/               # Context management feature
```

#### bootstrap.py

`bootstrap.py` is a utility script for initializing the database with data from CSV files. In the absence of a migrations system, it provides a reliable way to seed the environment for development and testing. This script is ideal for quickly setting up or resetting the database during local development or in CI pipelines.

You can run it with `python -m app.bootstrap` or import it as a module in other scripts.
By default, it drops all tables and recreates them before loading data, unless configured otherwise.

## Request Lifecycle

1. Request comes in with request_id for traceability.
2. Context + DB session created per request.
3. Route executes business logic.
4. On success → commit (auto-commit if outside a transaction).  
   On uncaught error → rollback.
5. Response returned (errors follow a common JSON envelope).

#### Error Envelope

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
└── conftest.py           # Shared test fixtures + scope set up
```

## 📊 API Endpoints

> Note: I'm not a fan of this, i think this is too verbose; but for now its a good starting point.

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
