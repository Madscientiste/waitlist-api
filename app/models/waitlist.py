from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Connection, ForeignKey, Integer, String, UniqueConstraint, event
from sqlalchemy.orm import Mapped, Mapper, mapped_column, relationship
from sqlalchemy.sql import func, select

from app.database.model import BaseModel

if TYPE_CHECKING:
    from app.models.offer import Offer
    from app.models.representation import Representation
    from app.models.user import User


class Waitlist(BaseModel):
    """
    Waitlist model representing a list of users waiting for tickets.
    Each waitlist can have multiple entries, each representing a user waiting for a specific ticket.
    """

    __tablename__ = "waitlists"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "offer_id",
            "representation_id",
            name="unique_user_waitlist",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)

    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False)
    offer_id: Mapped[str] = mapped_column(String, ForeignKey("offers.offer_id"), nullable=False)
    representation_id: Mapped[str] = mapped_column(String, ForeignKey("representations.id"), nullable=False)

    position: Mapped[int] = mapped_column(Integer, nullable=False)
    requested_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    # Relationships
    offer: Mapped["Offer"] = relationship("Offer", back_populates="waitlists")
    representation: Mapped["Representation"] = relationship("Representation", back_populates="waitlists")
    user: Mapped["User"] = relationship("User", back_populates="waitlists")


# Calculate the postion before inserting, using
# sqlachemy's pre_insert hook
@event.listens_for(Waitlist, "before_insert")
def before_insert(mapper: Mapper, connection: Connection, target: Waitlist):
    total_entries = connection.execute(
        select(func.count())
        .select_from(Waitlist)
        .where(
            Waitlist.offer_id == target.offer_id,
            Waitlist.representation_id == target.representation_id,
        )
    ).scalar()

    # eg, user_id = 1, offer_id = 1, representation_id = 1
    # now lets set the position to the total number of entries + 1
    target.position = total_entries + 1
