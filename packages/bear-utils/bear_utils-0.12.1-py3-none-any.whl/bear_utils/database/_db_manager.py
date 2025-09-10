"""Database Manager Module for managing database connections and operations."""

from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, ClassVar

from pydantic import SecretStr
from singleton_base import SingletonBase
from sqlalchemy import Engine, MetaData, create_engine
from sqlalchemy.orm import DeclarativeMeta, declarative_base, scoped_session, sessionmaker
from sqlalchemy.orm.session import Session

from bear_utils.database._db_config import DatabaseConfig, Schemas, from_db_url, get_default_config


class DatabaseManager:
    """A class to manage database connections and operations."""

    _bases: ClassVar[dict[str, DeclarativeMeta]] = {}
    _scoped_sessions: ClassVar[dict[str, scoped_session]] = {}
    _scheme: ClassVar[Schemas] = "sqlite"

    @classmethod
    def set_base(cls, base: DeclarativeMeta, name: str | None = None) -> None:
        """Set the base class for the database manager."""
        name = cls.__name__ if name is None else name
        cls._bases[name] = base

    @classmethod
    def get_base(cls, name: str | None = None) -> DeclarativeMeta:
        """Get the base class for the database manager."""
        name = cls.__name__ if name is None else name
        if name not in cls._bases:
            cls.set_base(declarative_base(), name)
        if name not in cls._bases:
            raise ValueError("Base class is not set, failed to set base.")
        return cls._bases[name]

    @classmethod
    def clear_bases(cls) -> None:
        """Clear all stored base classes."""
        cls._bases.clear()

    @classmethod
    def set_scheme(cls, scheme: Schemas) -> None:
        """Set the default scheme for the database manager."""
        cls._scheme = scheme

    def __init__(
        self,
        database_config: DatabaseConfig | None = None,
        host: str = "",
        port: int = 0,
        user: str = "",
        password: str | SecretStr = "",
        name: str = "",
        schema: Schemas | None = None,
        db_url: str | SecretStr | None = None,  # Deprecated
    ) -> None:
        """Initialize the DatabaseManager with a database URL or connection parameters."""
        database_config = from_db_url(db_url) if db_url else database_config  # backwards compatibility
        self.config: DatabaseConfig = database_config or get_default_config(
            schema=schema or self._scheme,
            host=host,
            port=port,
            name=name,
            user=user,
            password=password,
        )
        self.engine: Engine = create_engine(self.config.db_url.get_secret_value(), echo=False)
        base: DeclarativeMeta = DatabaseManager.get_base()
        self.metadata: MetaData = base.metadata
        self.SessionFactory: sessionmaker[Session] = sessionmaker(bind=self.engine)
        if self.db_id not in self._scoped_sessions:
            self._scoped_sessions[self.db_id] = scoped_session(self.SessionFactory)
        self.session: scoped_session[Session] = self._scoped_sessions[self.db_id]
        self.create_tables()

    @property
    def db_id(self) -> str:
        """Get the unique identity key for the database configuration."""
        return self.config.db_id

    def get_all_records[T_Table](self, table_obj: type[T_Table]) -> list[T_Table]:
        """Get all records from a table."""
        return self.session().query(table_obj).all()

    def count_records[T_Table](self, table_obj: type[T_Table]) -> int:
        """Count the number of records in a table."""
        return self.session().query(table_obj).count()

    def get_records_by_var[T_Table](self, table_obj: type[T_Table], variable: str, value: str) -> list[T_Table]:
        """Get records from a table by a specific variable."""
        return self.session().query(table_obj).filter(getattr(table_obj, variable) == value).all()

    def count_records_by_var[T_Table](self, table_obj: type[T_Table], variable: str, value: str) -> int:
        """Count the number of records in a table by a specific variable."""
        return self.session().query(table_obj).filter(getattr(table_obj, variable) == value).count()

    @contextmanager
    def open_session(self) -> Generator[Session, Any]:
        """Provide a transactional scope around a series of operations."""
        session: Session = self.session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

    def get_session(self) -> Session:
        """Get a new session."""
        return self.session()

    def close_session(self) -> None:
        """Close the session."""
        self.session.remove()

    def create_tables(self) -> None:
        """Create all tables defined by Base"""
        self.metadata.create_all(self.engine)

    def close_all(self) -> None:
        """Close all sessions and connections."""
        self.session.close()
        self.engine.dispose()


class SqliteDB(DatabaseManager):
    """SQLite Database Manager, inherits from DatabaseManager and sets the scheme to sqlite."""

    _scheme: ClassVar[Schemas] = "sqlite"


class PostgresDB(DatabaseManager):
    """Postgres Database Manager, inherits from DatabaseManager and sets the scheme to postgresql."""

    _scheme: ClassVar[Schemas] = "postgresql"


class MySQLDB(DatabaseManager):
    """MySQL Database Manager, inherits from DatabaseManager and sets the scheme to mysql."""

    _scheme: ClassVar[Schemas] = "mysql"


class SingletonDB(DatabaseManager, SingletonBase):
    """Singleton class for DatabaseManager, uses SingletonBase to inject singleton pattern."""

    _scheme: ClassVar[Schemas] = "sqlite"


__all__ = [
    "DatabaseManager",
    "MySQLDB",
    "PostgresDB",
    "SingletonDB",
    "SqliteDB",
]
