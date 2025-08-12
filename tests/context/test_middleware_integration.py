from app.context.app import get_app_context


def test_http_zone_set_via_middleware(app, client):
    captured = {}

    @app.get("/__test_ctx")
    async def __test_ctx_route():
        ctx = get_app_context()
        captured["path"] = ctx.http.get("path")
        captured["method"] = ctx.http.get("method")
        captured["request_id"] = ctx.http.get("request_id")
        return {"ok": True}

    response = client.get("/__test_ctx")
    assert response.status_code == 200

    assert captured["path"] == "/__test_ctx"
    assert captured["method"] == "GET"
    assert isinstance(captured["request_id"], str) and len(captured["request_id"]) > 0
