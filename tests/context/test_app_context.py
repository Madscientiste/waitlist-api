import pytest

from app.context.app import app_context, get_app_context


def test_get_app_context_raises_when_not_set():
    with pytest.raises(RuntimeError):
        get_app_context()


def test_app_context_sets_and_resets():
    with app_context() as ctx:
        current = get_app_context()
        assert current is ctx

    with pytest.raises(RuntimeError):
        get_app_context()


def test_nested_app_contexts_forbidden():
    with app_context() as outer_ctx:
        assert get_app_context() is outer_ctx
        with pytest.raises(RuntimeError):
            with app_context():
                pass

    with pytest.raises(RuntimeError):
        get_app_context()
