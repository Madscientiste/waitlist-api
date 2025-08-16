# Tests for exception handling and error response structure

from datetime import datetime

from fastapi.testclient import TestClient


def test_application_exception_response_structure(client: TestClient):
    """Test that application exceptions return proper error response structure.

    Since all custom exceptions inherit from BaseAppException, testing one validates the structure for all.
    Using invalid offer/representation IDs to trigger InvalidReferenceError (404).
    """
    response = client.get("/api/offers/nonexistent-offer/representations/nonexistent-repr/waitlist/test-user")

    assert response.status_code == 404
    data = response.json()

    # Verify error envelope structure
    assert "error" in data
    error = data["error"]

    # Required fields in error response
    required_fields = ["status", "code", "message", "timestamp", "request_id", "method", "path"]
    for field in required_fields:
        assert field in error, f"Missing required field: {field}"

    # Validate specific values; this route calls get_user_waitlist; which validates the user first
    assert error["status"] == "USER_DOES_NOT_EXIST"
    assert error["code"] == 404
    assert error["message"] == "User does not exist"
    assert error["method"] == "GET"
    assert "/offers/nonexistent-offer/representations/nonexistent-repr/waitlist/test-user" in error["path"]

    # Validate timestamp format (should be valid ISO datetime)
    timestamp = error["timestamp"]
    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))  # Should not raise exception

    # Details should be null for non-validation errors
    assert error["details"] is None


def test_validation_error_response_structure(client: TestClient):
    """Test FastAPI validation errors return proper error structure with details."""
    # Test invalid limit parameter on get_waitlist_entries endpoint
    response = client.get("/api/offers/test/representations/test/waitlist?limit=invalid")

    assert response.status_code == 422
    data = response.json()

    # Verify error envelope structure
    assert "error" in data
    error = data["error"]

    # Validation errors should have specific status and include details
    assert error["status"] == "VALIDATION_ERROR"
    assert error["code"] == 422
    assert error["message"] == "Validation failed"

    # Details should be present and contain validation errors
    assert "details" in error
    assert isinstance(error["details"], list)
    assert len(error["details"]) >= 1  # Should have error for invalid limit

    # Each detail should have validation error structure
    for detail in error["details"]:
        assert "loc" in detail
        assert "msg" in detail
        assert "type" in detail


def test_uncaught_exception_returns_generic_500(client: TestClient):
    """Test uncaught exceptions return generic 500 error response."""
    # Use the testing error endpoint that raises a generic Exception
    response = client.get("/api/error")

    assert response.status_code == 500
    data = response.json()

    # Verify error envelope structure
    assert "error" in data
    error = data["error"]

    # Uncaught exceptions should be converted to generic internal error
    assert error["status"] == "INTERNAL"
    assert error["code"] == 500
    assert error["message"] == "Internal Server Error"
    assert error["method"] == "GET"
    assert "/api/error" in error["path"]
    assert error["details"] is None
