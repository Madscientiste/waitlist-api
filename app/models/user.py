from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.model import BaseModel


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
