from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.model import BaseModel

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.inventory import Inventory
    from app.models.waitlist import Waitlist


class Offer(BaseModel):
    """
    Offer model representing ticket types available for events.
    Each event can have multiple offers (e.g., General Admission, VIP Package).
    """

    __tablename__ = "offers"

    offer_id: Mapped[str] = mapped_column(String, primary_key=True)
    event_id: Mapped[str] = mapped_column(String, ForeignKey("events.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    max_quantity_per_order: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="offers")
    inventory: Mapped[list["Inventory"]] = relationship("Inventory", back_populates="offer")
    waitlists: Mapped[list["Waitlist"]] = relationship("Waitlist", back_populates="offer")
