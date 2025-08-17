
import pytest

from app.database.connection import db
from app.exceptions.waitlist import (
    InvalidQuantityError,
    InvalidReferenceError,
    UserAlreadyOnWaitlistError,
    WaitlistNotAvailableError,
)
from app.repositories.waitlist import WaitlistRepository

repo = WaitlistRepository()


def test_join_waitlist_invalid_reference(user):
    """Test join_waitlist should raise InvalidReferenceError if entities do not exist"""
    with pytest.raises(InvalidReferenceError):
        repo.join_waitlist(
            user_id=user.id,
            offer_id="some_invalid_offer_id",
            representation_id="some_invalid_representation_id",
            quantity=2,
        )


def test_join_waitlist_available(user, event, representation, offer, available_inventory):
    """Test join_waitlist should raise WaitlistNotAvailableError if inventory is sold out"""
    with pytest.raises(WaitlistNotAvailableError):
        repo.join_waitlist(
            user_id=user.id,
            offer_id=offer.offer_id,
            representation_id=representation.id,
            quantity=2,
        )


def test_join_waitlist_invalid_quantity(user, event, representation, offer, sold_out_inventory):
    """Test join_waitlist should raise InvalidQuantityError if quantity is invalid"""
    with pytest.raises(InvalidQuantityError):
        repo.join_waitlist(
            user_id=user.id,
            offer_id=offer.offer_id,
            representation_id=representation.id,
            quantity=0,
        )

    # Also check for the case where the quantity is greater than the max quantity per order
    with pytest.raises(InvalidQuantityError):
        repo.join_waitlist(
            user_id=user.id,
            offer_id=offer.offer_id,
            representation_id=representation.id,
            quantity=5,
        )


def test_join_waitlist_success(user, event, representation, offer, sold_out_inventory):
    """Test join_waitlist should create a waitlist entry if the user is not already on the waitlist"""
    waitlist = repo.join_waitlist(
        user_id=user.id,
        offer_id=offer.offer_id,
        representation_id=representation.id,
        quantity=2,
    )

    assert waitlist is not None
    assert waitlist.user_id == user.id
    assert waitlist.offer_id == offer.offer_id
    assert waitlist.representation_id == representation.id
    assert waitlist.requested_quantity == 2


def test_join_waitlist_user_already_on_waitlist(user, event, representation, offer, sold_out_inventory):
    """Test join_waitlist should raise UserAlreadyOnWaitlistError if the user is already on the waitlist"""

    # First, create test data and first waitlist entry
    waitlist = repo.join_waitlist(
        user_id=user.id,
        offer_id=offer.offer_id,
        representation_id=representation.id,
        quantity=2,
    )

    assert waitlist is not None
    assert waitlist.user_id == user.id
    assert waitlist.offer_id == offer.offer_id

    # Expunge the waitlist object from the SQLAlchemy session to avoid warnings or session state issues.
    # This is necessary because the test checks for conflicts directly in the database,
    # Insert => then fail; instead of; SELECT => IF exist => fail.
    db.session.expunge(waitlist)

    with pytest.raises(UserAlreadyOnWaitlistError):
        repo.join_waitlist(
            user_id=user.id,
            offer_id=offer.offer_id,
            representation_id=representation.id,
            quantity=2,
        )
