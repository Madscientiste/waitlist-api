from __future__ import annotations

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.model import BaseModel


class Health(BaseModel):
    """
    The Health model exists solely as a 'hello world' for the backend.
    Its only purpose is to verify that the database, ORM, and project
    scaffolding are wired up and working. This is a placeholder model
    for initial setup and boilerplate validation—meant to be removed
    or replaced once real models are introduced.
    """

    __tablename__ = "healths"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    @staticmethod
    def create_health() -> Health:
        return Health().save()
