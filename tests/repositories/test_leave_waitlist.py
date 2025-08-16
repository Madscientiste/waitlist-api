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
    pass
