from app.database.connection import transaction
from app.models.health import Health


def test_save_commits_outside_transaction(session):
    h = Health().save()
    assert h.id is not None

    # Verify it is persisted and visible in a new session flush
    fetched = session.get(Health, h.id)
    assert fetched is not None


def test_save_flushes_inside_transaction(session):
    with transaction():
        h = Health().save()
        assert h.id is not None
        # Object should be queryable within the same transaction
        fetched = session.get(Health, h.id)
        assert fetched is not None
        # Do not commit here; rollback happens after context if exception is raised


def test_delete_outside_transaction(session):
    h = Health().save()
    hid = h.id

    h.delete()

    assert session.get(Health, hid) is None


def test_transaction_commit_and_rollback(session):
    # Commit on outermost
    with transaction():
        h1 = Health().save()
        assert session.get(Health, h1.id) is not None
    # After commit, it should still exist
    assert session.get(Health, h1.id) is not None

    # Rollback on error
    try:
        with transaction():
            h2 = Health().save()
            assert session.get(Health, h2.id) is not None
            raise RuntimeError("force rollback")
    except RuntimeError:
        pass

    # After rollback, h2 should not be persisted
    assert session.query(Health).order_by(Health.id.desc()).first().id == h1.id
