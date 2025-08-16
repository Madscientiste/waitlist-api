from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.model import BaseModel

if TYPE_CHECKING:
    from app.models.waitlist import Waitlist


class User(BaseModel):
    """
    Simple User model for waitlist functionality.
    In a real application, this would have authentication, profile data, etc.
    """

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    waitlists: Mapped[list["Waitlist"]] = relationship("Waitlist", back_populates="user")
