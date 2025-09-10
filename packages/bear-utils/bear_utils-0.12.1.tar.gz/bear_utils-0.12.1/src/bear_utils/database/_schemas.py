"""Database configuration schemas and defaults."""

from functools import cached_property
from hashlib import blake2b
from typing import Any, Literal, NamedTuple, Self

from pydantic import BaseModel, ConfigDict, Field, SecretStr

from bear_dereth.models.type_fields import Password

Schemas = Literal["sqlite", "postgresql", "mysql"]


class DBConfig(NamedTuple):
    """Information about a database schema."""

    name: str | None = None
    host: str | None = None
    port: int | None = None
    username: str | None = None
    password: str | Password | None = Password(None)


class DefaultDBConfig:
    sqlite: DBConfig = DBConfig(name="database.db")
    postgresql: DBConfig = DBConfig(name="postgres", host="localhost", port=5432, username="postgres")
    mysql: DBConfig = DBConfig(name="mysql", host="localhost", port=3306, username="root")

    @classmethod
    def get(cls, scheme: Schemas) -> DBConfig:
        """Get the default database configuration for a given scheme."""
        return getattr(cls, scheme)


class DatabaseConfig(BaseModel):
    """Configuration for paths used in the application."""

    scheme: Schemas
    host: str | None = None
    port: int | None = Field(default=None, ge=0, le=65535)
    name: str | None = None
    username: str | None = None
    password: Password | None = Field(default=Password(None))

    model_config = ConfigDict(frozen=True)

    def model_post_init(self, context: Any) -> None:
        """Set default values for missing fields based on the scheme."""
        defaults: DBConfig = DefaultDBConfig.get(self.scheme)
        match self.scheme:
            case "sqlite":
                if self.name in (None, ""):
                    self.name = defaults.name
            case "postgresql" | "mysql":
                if self.host in (None, ""):
                    self.host = defaults.host
                if self.name in (None, ""):
                    self.name = defaults.name
                if self.port in (None, 0):
                    self.port = defaults.port
                if self.username in (None, ""):
                    self.username = defaults.username
            case _:
                raise ValueError(f"Unsupported database scheme: {self.scheme}")
        return super().model_post_init(context)

    @cached_property
    def db_url(self) -> SecretStr:
        """Get the database URL as a SecretStr since it may contain a password.

        This is a little paranoid but it's better than to accidentally log a password.

        Example:
            ``postgresql://user:password@localhost:5432/dbname``

            ``mysql://user:password@localhost:3306/dbname``

            ``sqlite:///path/to/database.db``

        Returns:
            SecretStr: The database URL as a SecretStr, you will need to call
            get_secret_value() to get the string.
        """
        url: str = f"{self.scheme}://"
        if self.username not in (None, ""):
            url += self.username
            if self.password and not self.password.is_null():
                url += f":{self.password.get_secret_value()}"
            url += "@"
        if self.host:
            url += self.host
        if self.port:
            url += f":{self.port}"
        if self.name:
            url += f"/{self.name}"
        return SecretStr(url)

    @cached_property
    def db_id(self) -> str:
        """Get a unique identity key for the database configuration.

        This is to allow for scoped sessions based on the database configuration. They
        should be used as a key in a dictionary, so we use a hash of the database data.
        """
        return blake2b(self.db_url.get_secret_value().encode("utf-8"), digest_size=10).hexdigest()

    @classmethod
    def by_schema(
        cls,
        scheme: Schemas,
        host: str | None = None,
        port: int | None = None,
        name: str | None = None,
        username: str | None = None,
    ) -> Self:
        """Create a DatabaseConfig with default values for the given scheme."""
        defaults: DBConfig = DefaultDBConfig.get(scheme)
        return cls(
            scheme=scheme,
            host=host or defaults.host,
            port=port or defaults.port,
            name=name or defaults.name,
            username=username or defaults.username,
        )


__all__ = ["DatabaseConfig"]
