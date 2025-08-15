import pytest
from fastapi.testclient import TestClient

from app.config import app_config
from app.database.connection import db


@pytest.fixture(scope="session", autouse=True)
def setup_environment():
    # Ensure tests in this package use SQLite regardless of global env
    app_config.ENVIRONMENT = "testing"


@pytest.fixture()
def session():
    # Clean session per test
    yield db.session
    try:
        db.session.rollback()
    except Exception:
        pass
    db.session.close()


@pytest.fixture()
def app():
    from app.api.app import app as fastapi_app

    return fastapi_app


@pytest.fixture()
def client(app):
    return TestClient(app)


# Note: Table creation is currently handled by FastAPI's startup event,
# so explicit setup here is skipped for API tests. For direct database/model tests,
# ensure tables are created before running tests. Improving this setup for more
# robust and isolated test environments is recommended in the future.
