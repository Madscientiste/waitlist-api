from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, Generator, Optional
from uuid import uuid4

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker

from app.config import app_config

_tx_token = ContextVar("tx_token", default=None)


class Database:
    """Sets up and manages the database connection.

    This class manages the connection to a PostgreSQL database and provides methods
    for creating and managing database sessions within a specific scope (like a request).

    - Copied from: https://github.com/acidjunk/fastapi-postgres-boilerplate/blob/4f6f88dd8cf5cad2238530b3c1a91970d524bbb5/server/db/database.py
    """

    def __init__(self):
        """Initializes the database connection manager.

        This method creates the following:

        * `request_context`: A `ContextVar` object to store a unique identifier for
          the current request/scope.
        * `engine`: A SQLAlchemy engine object representing the database connection.
        * `session_factory`: A factory function that creates new SQLAlchemy session objects.
        * `scoped_session`: A thread-local session object that provides database sessions
          within a specific scope.
        """

        self.request_context: ContextVar[str] = ContextVar(
            "request_context",
            default="",
        )
        self.engine = create_engine(
            **app_config.ENGINE_ARGUMENTS,
        )
        self.session_factory = sessionmaker(
            bind=self.engine,
            **app_config.SESSION_ARGUMENTS,
        )
        self.scoped_session = scoped_session(
            self.session_factory,
            self._scopefunc,
        )

    def _scopefunc(self) -> Optional[str]:
        """Retrieves the current scope identifier from the request_context.

        This method is used internally by the `scoped_session` to identify the current
        database session scope.
        """

        return self.request_context.get()

    def set_engine(self, engine: Engine):
        """Sets a new engine and updates the session factory and scoped session."""
        self.engine = engine
        self.session_factory = sessionmaker(
            bind=self.engine,
            **app_config.SESSION_ARGUMENTS,
        )
        self.scoped_session = scoped_session(
            self.session_factory,
            self._scopefunc,
        )

    @property
    def session(self) -> Session:
        """Returns the current database session.

        This property provides access to the current database session within the active scope.
        """

        return self.scoped_session()

    @contextmanager
    def scope(self, **kwargs: ...) -> Generator["Database", None, None]:
        """Creates a new database session within a specific scope.

        This context manager is used to create a new database session for a specific scope
        (like a request or workflow).

        * Sets a unique identifier for the scope using `uuid4()`.
        * Creates a new session using the `scoped_session` with optional arguments passed
          to the context manager.
        * Yields control back to the caller within the scope.
        * After exiting the scope (using `with`), removes the session and resets the context
          identifier.

        Args:
          kwargs: Optional session arguments to be passed to the created session.
        """

        token = self.request_context.set(str(uuid4()))
        self.scoped_session(**kwargs)

        try:
            yield self
        except Exception as e:
            raise e from e
        finally:
            self.scoped_session.remove()
            try:
                self.request_context.reset(token)
            except (RuntimeError, ValueError):
                pass  # Silently ignore if context changed


def is_in_transaction():
    """Check if currently in a transaction block with fallbacks"""
    return _tx_token.get() is not None


@contextmanager
def transaction():
    """Global transaction context manager with safeguards against leaks"""
    tx_id = str(uuid4())
    token = _tx_token.set(tx_id)

    try:
        yield
        # Only commit if we're in the outermost transaction
        if _tx_token.get() == tx_id:
            db.session.commit()
    except Exception as e:
        # Only rSQLAlchemyollback if we're in the outermost transaction
        if _tx_token.get() == tx_id:
            db.session.rollback()
        raise e
    finally:
        try:
            _tx_token.reset(token)
        except (RuntimeError, ValueError):
            pass  # Silently ignore if context changed


@contextmanager
def savepoint():
    """Create a savepoint that can be rolled back independently"""
    if not is_in_transaction():
        raise RuntimeError("Savepoints can only be used within a transaction")

    savepoint = db.session.begin_nested()

    try:
        yield savepoint
        savepoint.commit()
    except Exception as e:
        savepoint.rollback()
        raise e


class TransactionDescriptor:
    def __get__(self, instance: Any, owner: Any) -> bool:
        return is_in_transaction()


class SessionDescriptor:
    def __get__(self, instance: Any, owner: Any) -> Session:
        return db.session


db = Database()
