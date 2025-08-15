from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.model import BaseModel

if TYPE_CHECKING:
    from app.models.offer import Offer
    from app.models.representation import Representation
    from app.models.waitlist import Waitlist


class Event(BaseModel):
    """
    Event model representing concerts, shows, and other performances.
    Each event can have multiple representations (show times) and offers (ticket types).
    """

    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=True)
    thumbnail_url: Mapped[str] = mapped_column(String, nullable=True)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)
    venue_name: Mapped[str] = mapped_column(String, nullable=False)
    venue_address: Mapped[str] = mapped_column(String, nullable=False)
    timezone: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    representations: Mapped[list["Representation"]] = relationship("Representation", back_populates="event")
    offers: Mapped[list["Offer"]] = relationship("Offer", back_populates="event")
