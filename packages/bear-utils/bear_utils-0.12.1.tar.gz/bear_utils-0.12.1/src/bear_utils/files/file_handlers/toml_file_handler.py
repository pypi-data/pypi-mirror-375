"""TOML File Handler Module"""

from pathlib import Path
import tomllib
from typing import Any, ClassVar, Self

from pydantic import BaseModel
import tomli_w

from bear_utils.files.file_handlers._base_file_handler import FileHandler


class TomlFileHandler(FileHandler):
    """Class for handling .toml files with read, write, and present methods"""

    valid_extensions: ClassVar[list[str]] = ["toml"]
    valid_types: ClassVar[tuple[type, ...]] = (dict, str)

    def read_file(self, file_path: Path) -> dict:
        """Read a TOML file and return its content as a dictionary."""
        try:
            super().verify_file(file_path)
            with open(file_path, "rb") as file:
                return tomllib.load(file)
        except Exception as e:
            raise ValueError(f"Error reading file: {e}") from e

    def write_file(self, file_path: Path, data: dict[str, Any] | str, mkdir: bool = False, **kwargs) -> None:
        """Write data to a TOML file."""
        try:
            super().verify_write_file(file_path=file_path, data=data, mkdir=mkdir)
            output: str = tomli_w.dumps(data) if isinstance(data, dict) else data
            file_path.write_text(output, **kwargs)
        except Exception as e:
            raise ValueError(f"Error writing file: {e}") from e

    def present_file(self, data: dict[str, Any] | str, **_) -> str:
        """Present data as a string."""
        # TODO: Actually implement this method to format TOML data nicely
        return str(data)

    def model_to_toml(self, model: BaseModel, exclude_none: bool = True, **kwargs) -> str:
        """Convert a Pydantic model to TOML format.

        Args:
            model: Pydantic BaseModel instance to convert.
            exclude_none: Whether to exclude fields with None values.
            **kwargs: Additional keyword arguments to pass to model_dump.

        Returns:
            str: TOML formatted string of the model data.
        """
        return tomli_w.dumps(model.model_dump(exclude_none=exclude_none, **kwargs))


class PyProjectToml(BaseModel):
    """Dataclass for handling pyproject.toml files"""

    name: str
    version: str | None = None
    dynamic: list[str] | None = None
    description: str | None = None
    author_name: str | None = None
    author_email: str | None = None
    dependencies: list[str] | None = None

    def model_post_init(self, context: Any) -> None:
        """Post-initialization processing to clean up dependencies."""
        if self.dependencies:
            self.dependencies = [dep.split(" ")[0] for dep in self.dependencies if isinstance(dep, str)]
            self.dependencies = [dep.split(">=")[0] for dep in self.dependencies]
        return super().model_post_init(context)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a PyProjectToml instance from a dictionary."""
        data = data.get("project", {})
        authors: dict = data.get("authors", {})[0]
        return cls(
            name=data.get("name", ""),
            version=data.get("version", ""),
            description=data.get("description"),
            author_name=authors.get("name") if authors else None,
            author_email=authors.get("email") if authors else None,
            dependencies=data.get("dependencies", []),
        )
