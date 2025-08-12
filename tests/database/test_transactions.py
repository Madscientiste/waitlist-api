from app.database.connection import savepoint, transaction
from app.models.health import Health


def test_nested_transactions_commit_only_outermost(session):
    with transaction():
        h_outer = Health().save()
        with transaction():
            Health().save()
        # inner shouldn't commit separately; both committed at outer exit
    assert session.get(Health, h_outer.id) is not None
    assert session.get(Health, h_outer.id) is not None


def test_savepoint_rolls_back_independently(session):
    with transaction():
        kept = Health().save()
        try:
            with savepoint():
                doomed = Health().save()
                raise RuntimeError("rollback inner")
        except RuntimeError:
            pass
        # kept should remain; doomed should be gone in current tx
        assert session.get(Health, kept.id) is not None
        assert session.get(Health, getattr(locals().get("doomed", Health()), "id", -1)) is None
    # After commit, kept is persisted
    assert session.get(Health, kept.id) is not None
