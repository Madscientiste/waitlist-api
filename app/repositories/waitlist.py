from __future__ import annotations

from typing import List, Optional

from sqlalchemy.exc import IntegrityError

from app.exceptions.waitlist import (
    InvalidQuantityError,
    InvalidReferenceError,
    UserAlreadyOnWaitlistError,
    UserDoesNotExistError,
    UserNotOnWaitlistError,
    WaitlistNotAvailableError,
)
from app.models.inventory import Inventory
from app.models.offer import Offer
from app.models.representation import Representation
from app.models.user import User
from app.models.waitlist import Waitlist


class WaitlistRepository:
    """
    Repository for waitlist operations.
    Handles business logic and database operations for waitlist management.
    """

    def join_waitlist(self, user_id: str, offer_id: str, representation_id: str, quantity: int) -> Waitlist:
        """
        Join a waitlist for a specific offer/representation combination.

        Args:
            user_id: ID of the user joining the waitlist
            offer_id: ID of the offer (ticket type)
            representation_id: ID of the representation (show time)
            quantity: Number of tickets requested

        Returns:
            Waitlist entry with calculated position

        Raises:
            UserAlreadyOnWaitlistError: User is already on this waitlist
            InvalidReferenceError: Invalid offer/representation/event
            InvalidQuantityError: Quantity exceeds limits or is invalid
            WaitlistNotAvailableError: Waitlist not active (tickets still available)
        """
        # 0. Validate user exists
        if not self._validate_user_exists(user_id):
            raise UserDoesNotExistError()

        # 1. Validate entities exist
        if not self._validate_entities_exist(offer_id, representation_id):
            raise InvalidReferenceError()

        # 2. Check if waitlist is available (inventory sold out)
        if not self.is_waitlist_available(offer_id, representation_id):
            raise WaitlistNotAvailableError()

        # 3. Validate quantity
        if quantity <= 0:
            raise InvalidQuantityError("Quantity must be greater than 0")

        offer = self._get_offer(offer_id)
        if quantity > offer.max_quantity_per_order:
            raise InvalidQuantityError(f"Quantity exceeds maximum of {offer.max_quantity_per_order}")

        try:
            # Try to insert the waitlist entry directly, relying on the database's unique constraint
            # minimizing round-trips.
            waitlist = Waitlist(
                id=f"wait_{user_id}_{offer_id}_{representation_id}",  # Simple ID generation
                user_id=user_id,
                offer_id=offer_id,
                representation_id=representation_id,
                requested_quantity=quantity,
            ).save()

            return waitlist

        except IntegrityError:
            # When IntegrityError occurs during flush(), the session becomes dirty and needs rollback
            # This handles the UNIQUE constraint violation for (user_id, offer_id, representation_id)

            Waitlist.session.rollback()
            raise UserAlreadyOnWaitlistError()

    def get_user_waitlist(self, user_id: str, offer_id: str, representation_id: str) -> Waitlist:
        """
        Get a user's waitlist entry for a specific offer/representation.

        Args:
            user_id: ID of the user
            offer_id: ID of the offer
            representation_id: ID of the representation

        Returns:
            Waitlist entry

        Raises:
            UserNotOnWaitlistError: User is not on this waitlist
            InvalidReferenceError: Invalid offer/representation/event
            UserDoesNotExistError: User does not exist
        """

        # 0. Validate user exists
        if not self._validate_user_exists(user_id):
            raise UserDoesNotExistError()

        # 1. Validate entities exist
        if not self._validate_entities_exist(offer_id, representation_id):
            raise InvalidReferenceError()

        # 2. Get waitlist entry
        waitlist_entry = (
            Waitlist.session.query(Waitlist)
            .filter(Waitlist.user_id == user_id, Waitlist.offer_id == offer_id, Waitlist.representation_id == representation_id)
            .first()
        )

        if not waitlist_entry:
            raise UserNotOnWaitlistError()

        return waitlist_entry

    def get_waitlist_entries(self, offer_id: str, representation_id: str, limit: int = 50, page: int = 0) -> List[Waitlist]:
        """
        Get all waitlist entries for a specific offer/representation, ordered by position.

        Args:
            offer_id: ID of the offer
            representation_id: ID of the representation
            limit: Maximum number of entries to return
            page: Page number

        Returns:
            List of waitlist entries ordered by position

        Raises:
            InvalidReferenceError: Invalid offer/representation/event
        """
        # Validate entities exist
        if not self._validate_entities_exist(offer_id, representation_id):
            raise InvalidReferenceError()

        return (
            Waitlist.session.query(Waitlist)
            .filter(Waitlist.offer_id == offer_id, Waitlist.representation_id == representation_id)
            .order_by(Waitlist.position)
            .limit(limit)
            .offset(page * limit)
            .all()
        )

    def get_waitlist_entries_count(self, offer_id: str, representation_id: str) -> int:
        """
        Get total count of waitlist entries for a specific offer/representation.

        Args:
            offer_id: ID of the offer
            representation_id: ID of the representation

        Returns:
            Total number of waitlist entries

        Raises:
            InvalidReferenceError: Invalid offer/representation/event
        """
        # Validate entities exist
        if not self._validate_entities_exist(offer_id, representation_id):
            raise InvalidReferenceError()

        return (
            Waitlist.session.query(Waitlist)
            .filter(Waitlist.offer_id == offer_id, Waitlist.representation_id == representation_id)
            .count()
        )

    def get_next_in_line(self, offer_id: str, representation_id: str) -> Optional[Waitlist]:
        """
        Get the next person in line for a specific offer/representation.

        Args:
            offer_id: ID of the offer
            representation_id: ID of the representation

        Returns:
            Waitlist entry with position 1, or None if waitlist is empty

        Raises:
            InvalidReferenceError: Invalid offer/representation/event
        """
        # Validate entities exist
        if not self._validate_entities_exist(offer_id, representation_id):
            raise InvalidReferenceError()

        return (
            Waitlist.session.query(Waitlist)
            .filter(Waitlist.offer_id == offer_id, Waitlist.representation_id == representation_id)
            .order_by(Waitlist.position)
            .first()
        )

    def leave_waitlist(self, user_id: str, offer_id: str, representation_id: str) -> bool:
        """
        Remove a user from a waitlist.

        Args:
            user_id: ID of the user leaving
            offer_id: ID of the offer
            representation_id: ID of the representation

        Returns:
            True if successfully left, False if not found

        Raises:
            UserNotOnWaitlistError: User is not on this waitlist
            InvalidReferenceError: Invalid offer/representation/event
            UserDoesNotExistError: User does not exist
        """

        # 0. Validate user exists
        if not self._validate_user_exists(user_id):
            raise UserDoesNotExistError()

        # 1. Validate entities exist
        if not self._validate_entities_exist(offer_id, representation_id):
            raise InvalidReferenceError()

        # 2. Get waitlist entry and delete it
        waitlist = self.get_user_waitlist(user_id, offer_id, representation_id)
        waitlist.delete()
        return True

    def is_waitlist_available(self, offer_id: str, representation_id: str) -> bool:
        """
        Check if waitlist is available for a specific offer/representation.
        Waitlist is available when inventory is sold out.

        Args:
            offer_id: ID of the offer
            representation_id: ID of the representation

        Returns:
            True if waitlist is available, False otherwise
        """
        inventory = self._get_inventory(offer_id, representation_id)

        # Waitlist is available when inventory is sold out
        return inventory is not None and inventory.available_stock == 0

    def _validate_user_exists(self, user_id: str) -> bool:
        """
        Validate that the user exists.
        """
        return User.session.query(User).filter(User.id == user_id).first() is not None

    def _validate_entities_exist(self, offer_id: str, representation_id: str) -> bool:
        """
        Validate that the offer and representation exist.

        Args:
            offer_id: ID of the offer to validate
            representation_id: ID of the representation to validate

        Returns:
            True if both entities exist, False otherwise
        """
        offer = self._get_offer(offer_id)
        if not offer:
            raise InvalidReferenceError(message=f"Offer {offer_id} does not exist")

        representation = self._get_representation(representation_id)
        if not representation:
            raise InvalidReferenceError(message=f"Representation {representation_id} does not exist")

        return True

    def _get_offer(self, offer_id: str) -> Optional[Offer]:
        """
        Get an offer by ID.

        Args:
            offer_id: ID of the offer

        Returns:
            Offer object if found, None otherwise
        """
        return Offer.session.query(Offer).filter(Offer.offer_id == offer_id).first()

    def _get_representation(self, representation_id: str) -> Optional[Representation]:
        """
        Get a representation by ID.

        Args:
            representation_id: ID of the representation

        Returns:
            Representation object if found, None otherwise
        """
        return Representation.session.query(Representation).filter(Representation.id == representation_id).first()

    def _get_inventory(self, offer_id: str, representation_id: str) -> Optional[Inventory]:
        """
        Get inventory for a specific offer/representation combination.

        Args:
            offer_id: ID of the offer
            representation_id: ID of the representation

        Returns:
            Inventory object if found, None otherwise
        """
        return (
            Inventory.session.query(Inventory)
            .filter(
                Inventory.offer_id == offer_id,
                Inventory.representation_id == representation_id,
            )
            .first()
        )
