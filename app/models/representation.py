from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.model import BaseModel

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.inventory import Inventory
    from app.models.waitlist import Waitlist


class Representation(BaseModel):
    """
    Representation model representing show times/performances for events.
    Each event can have multiple representations (e.g., Friday 8PM, Saturday 2PM).
    """

    __tablename__ = "representations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    event_id: Mapped[str] = mapped_column(String, ForeignKey("events.id"), nullable=False)
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="representations")
    inventory: Mapped[list["Inventory"]] = relationship("Inventory", back_populates="representation")
    waitlists: Mapped[list["Waitlist"]] = relationship("Waitlist", back_populates="representation")
