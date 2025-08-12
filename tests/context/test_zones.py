import pytest

from app.context.app import app_context, get_app_context


def test_http_zone_sets_and_clears_data():
    with app_context() as ctx:
        with ctx.http(path="/x", method="GET", request_id="rid-1"):
            http = get_app_context().http
            assert http["path"] == "/x"
            assert http.get("method") == "GET"
            assert http.get("request_id") == "rid-1"
            assert "path" in http

        # cleared after exit
        http = get_app_context().http
        assert http.get("path") is None
        assert "path" not in http


def test_cli_zone_sets_and_clears_data():
    with app_context() as ctx:
        with ctx.cli(command="rebuild-index"):
            cli = get_app_context().cli
            assert cli["command"] == "rebuild-index"
            assert cli.get("command") == "rebuild-index"
            assert "command" in cli

        cli = get_app_context().cli
        assert cli.get("command") is None
        assert ("command" in cli) is False


def test_http_zone_missing_key_raises_on_getitem():
    with app_context() as ctx:
        with ctx.http(path="/y", method="POST", request_id="rid-2"):
            pass

        http = get_app_context().http
        with pytest.raises(KeyError):
            _ = http["nonexistent"]


def test_zone_nesting_is_forbidden():
    """
    Forbid nesting to avoid misuse and subtle leakage.
    """

    with app_context() as ctx:
        with ctx.http(path="/a", method="GET", request_id="r1"):
            assert get_app_context().http["path"] == "/a"
            with pytest.raises(RuntimeError):
                with ctx.http(path="/b", method="POST", request_id="r2"):
                    pass
