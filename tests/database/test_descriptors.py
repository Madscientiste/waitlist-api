from app.database.connection import db, transaction
from app.models.health import Health


def test_session_descriptor_matches_db_session(session):
    assert Health.session is db.session


def test_is_in_transaction_descriptor_toggles(session):
    assert Health.is_in_transaction is False
    with transaction():
        assert Health.is_in_transaction is True
    assert Health.is_in_transaction is False
