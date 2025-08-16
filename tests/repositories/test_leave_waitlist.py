import pytest

from app.exceptions.waitlist import (
    InvalidReferenceError,
    UserDoesNotExistError,
    UserNotOnWaitlistError,
)
from app.repositories.waitlist import WaitlistRepository

repo = WaitlistRepository()


def test_leave_waitlist_success(user, event, representation, offer, sold_out_inventory):
    """Test leave_waitlist should successfully remove user from waitlist"""
    # First join the waitlist
    waitlist = repo.join_waitlist(
        user_id=user.id,
        offer_id=offer.offer_id,
        representation_id=representation.id,
        quantity=2,
    )
    assert waitlist is not None
    assert waitlist.position == 1

    # Then leave the waitlist
    result = repo.leave_waitlist(
        user_id=user.id,
        offer_id=offer.offer_id,
        representation_id=representation.id,
    )

    assert result is True

    # Verify user is no longer on waitlist
    with pytest.raises(UserNotOnWaitlistError):
        repo.get_user_waitlist(
            user_id=user.id,
            offer_id=offer.offer_id,
            representation_id=representation.id,
        )


def test_leave_waitlist_user_not_on_waitlist(user, event, representation, offer, sold_out_inventory):
    """Test leave_waitlist should raise UserNotOnWaitlistError if user is not on waitlist"""
    with pytest.raises(UserNotOnWaitlistError):
        repo.leave_waitlist(
            user_id=user.id,
            offer_id=offer.offer_id,
            representation_id=representation.id,
        )


def test_leave_waitlist_invalid_references(user):
    """Test leave_waitlist should raise InvalidReferenceError for invalid offer/representation"""
    with pytest.raises(InvalidReferenceError):
        repo.leave_waitlist(
            user_id=user.id,
            offer_id="invalid_offer_id",
            representation_id="invalid_representation_id",
        )


def test_leave_waitlist_user_does_not_exist(event, representation, offer, sold_out_inventory):
    """Test leave_waitlist should raise UserDoesNotExistError if user does not exist"""
    with pytest.raises(UserDoesNotExistError):
        repo.leave_waitlist(
            user_id="non_existent_user",
            offer_id=offer.offer_id,
            representation_id=representation.id,
        )


def test_leave_waitlist_with_multiple_users(event, representation, offer, sold_out_inventory):
    """Test leave_waitlist works correctly when multiple users are on waitlist"""
    from app.models.user import User

    # Create multiple users
    user1 = User(id="user_001", email="user1@test.com", first_name="User", last_name="One").save()
    user2 = User(id="user_002", email="user2@test.com", first_name="User", last_name="Two").save()
    user3 = User(id="user_003", email="user3@test.com", first_name="User", last_name="Three").save()

    # All users join waitlist
    waitlist1 = repo.join_waitlist(user1.id, offer.offer_id, representation.id, 1)
    waitlist2 = repo.join_waitlist(user2.id, offer.offer_id, representation.id, 1)
    waitlist3 = repo.join_waitlist(user3.id, offer.offer_id, representation.id, 1)

    # Verify positions
    assert waitlist1.position == 1
    assert waitlist2.position == 2
    assert waitlist3.position == 3

    # User 2 leaves (middle position)
    result = repo.leave_waitlist(user2.id, offer.offer_id, representation.id)
    assert result is True

    # Verify user2 is no longer on waitlist
    with pytest.raises(UserNotOnWaitlistError):
        repo.get_user_waitlist(user2.id, offer.offer_id, representation.id)

    # Verify other users still exist with their original positions
    # (No reordering as per FIFO requirements)
    remaining_user1 = repo.get_user_waitlist(user1.id, offer.offer_id, representation.id)
    remaining_user3 = repo.get_user_waitlist(user3.id, offer.offer_id, representation.id)

    assert remaining_user1.position == 1
    assert remaining_user3.position == 3

    # Verify get_next_in_line still returns user1 (position 1)
    next_in_line = repo.get_next_in_line(offer.offer_id, representation.id)
    assert next_in_line.user_id == user1.id
    assert next_in_line.position == 1
