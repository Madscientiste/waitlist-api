from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, ClassVar, Generic, TypeVar

from sqlalchemy import JSON, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.database.connection import TransactionDescriptor

from .connection import Session, SessionDescriptor

T = TypeVar("T", bound="BaseModel")


class BaseModelMeta(type(DeclarativeBase)):
    def __new__(cls, name: str, bases: tuple[Any], attrs: dict[str, Any], **kwargs: ...):
        super_new = super().__new__

        # Ensure initialization is only performed for
        # subclasses of Model (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, BaseModelMeta)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        new_class = super().__new__(cls, name, bases, attrs, **kwargs)

        # Descriptors ensure that session and is_in_transaction always
        # resolve to the correct value for the current context/request,
        # rather than being shared or static across all usages.
        #
        # Also, its nice to NOT import the session each time we need it.
        new_class.add_to_class("session", SessionDescriptor())
        new_class.add_to_class("is_in_transaction", TransactionDescriptor())

        # This is where manager (queryset) implementations would go.
        # For example, you could use:
        #
        #   # Get a post by ID
        #   post = Post.objects.get(id=5)
        #
        #   # Get the most recent published post by a specific author
        #   latest_post = Post.objects.filter(
        #       author__username="johndoe",
        #       status="published"
        #   ).order_by("-published_at").first()
        #
        # However, due to time constraints, this feature is not implemented in this project.

        # Don't forget to return the new class.... ( because i did, not fun to debug )
        return new_class

    def add_to_class(cls, name: str, value: Any) -> None:
        """Adds a property to the class"""
        setattr(cls, name, value)


class BaseModel(DeclarativeBase, Generic[T], metaclass=BaseModelMeta):
    __abstract__ = True

    session: ClassVar[Session]
    is_in_transaction: ClassVar[bool]

    type_annotation_map = {dict[str, Any]: JSON}

    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    updated: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    def _handle_transaction(self):
        if self.is_in_transaction:
            # In transaction: just flush to send to DB, let transaction() handle commit
            self.session.flush()
        else:
            # Not in transaction: commit immediately (includes flush)
            self.session.commit()

    def save(self):
        self.session.add(self)

        self._handle_transaction()

        # Refresh to get any DB-generated values (like IDs, timestamps)
        self.session.refresh(self)
        return self

    def delete(self):
        self.session.delete(self)

        self._handle_transaction()

        return self
