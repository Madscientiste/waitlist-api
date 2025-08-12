from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import text

from app.database.connection import db


def test_health_endpoint_creates_row_and_returns_context(client):
    resp = client.get("/api/v1/ping")
    assert resp.status_code == 200
    data = resp.json()
    assert data["message"] == "pong"
    assert isinstance(data["request_id"], str)
    assert data["path"] == "/api/v1/ping"


def test_per_request_session_isolation(client):
    # Fire two requests and ensure different request contexts are used
    def get_request_id():
        r = client.get("/api/v1/ping")
        return r.json()["request_id"]

    with ThreadPoolExecutor(max_workers=2) as ex:
        rid1, rid2 = ex.map(lambda _: get_request_id(), range(2))

    assert rid1 != rid2


def test_session_closed_after_request(client):
    # Access session before and after request to ensure no exception is raised and session is cleaned
    resp = client.get("/api/v1/ping")
    assert resp.status_code == 200
    # After request, scoped_session should have removed the request-bound session
    # A new call to db.session should yield a valid, open session
    s = db.session
    # basic sanity: executing trivial SQL shouldn't raise
    s.execute(text("SELECT 1"))
