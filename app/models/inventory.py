from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.model import BaseModel

if TYPE_CHECKING:
    from app.models.offer import Offer
    from app.models.representation import Representation


class Inventory(BaseModel):
    """
    Inventory model representing stock levels for specific offer and representation combinations.
    Each representation/offer combination has its own inventory record.
    """

    __tablename__ = "inventory"

    inventory_id: Mapped[str] = mapped_column(String, primary_key=True)
    offer_id: Mapped[str] = mapped_column(String, ForeignKey("offers.offer_id"), nullable=False)
    representation_id: Mapped[str] = mapped_column(String, ForeignKey("representations.id"), nullable=False)
    total_stock: Mapped[int] = mapped_column(Integer, nullable=False)
    available_stock: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    offer: Mapped["Offer"] = relationship("Offer", back_populates="inventory")
    representation: Mapped["Representation"] = relationship("Representation", back_populates="inventory")
