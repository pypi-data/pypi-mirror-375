"""A module for handling file ignore patterns and directories in Bear Utils."""

from contextlib import suppress
from dataclasses import dataclass, field
import os
from pathlib import Path
from typing import Literal, Self

from pathspec import PathSpec
from rich.prompt import Confirm

from bear_dereth.constants.enums.log_level import LogLevel
from bear_utils.logger_manager import ConsoleLogger

IGNORE_PATTERNS: list[str] = [
    "**/__pycache__",
    ".git",
    "**/.venv",
    ".env",
    ".vscode",
    ".idea",
    "*.DS_Store*",
    "__pypackages__",
    ".pytest_cache",
    ".coverage",
    ".*.swp",
    ".*.swo",
    "*.lock",
    "dist/",
    "**/.nox",
    "**/.pytest_cache",
    "**/.ruff_cache",
]

IGNORE_COUNT = 100


@dataclass(slots=True)
class IgnoreContainer:
    """Container for ignored and non-ignored paths."""

    non_ignored: list[Path] = field(default_factory=list)
    ignored: list[Path] = field(default_factory=list)

    @property
    def non_ignored_count(self) -> int:
        """Get the count of non-ignored paths."""
        return len(self.non_ignored)

    @property
    def ignored_count(self) -> int:
        """Get the count of ignored paths."""
        return len(self.ignored)

    @classmethod
    def store_result(cls, value: tuple[list[Path], list[Path]]) -> Self:
        """Set the ignored and non-ignored paths from a tuple."""
        return cls(*value)


class IgnoreHandler:
    """Basic ignore handler for manually checking if a file should be ignored based on set patterns."""

    def __init__(self, ignore_file: Path | None = None, combine: bool = False, verbose: bool = False) -> None:
        """Initialize the IgnoreHandler with an optional ignore file."""
        self.ignore_file: Path | None = ignore_file
        self.patterns: list[str] = self.load_patterns(ignore_file, combine) if ignore_file else IGNORE_PATTERNS
        self.spec: PathSpec = self._create_spec(self.patterns)
        self.logger: ConsoleLogger = ConsoleLogger.get_instance(init=True)
        self.logger.set_base_level(LogLevel.VERBOSE if verbose else LogLevel.INFO)
        self.output: bool = True

    @staticmethod
    def _create_spec(patterns: list[str]) -> PathSpec:
        """Create a pathspec from the given patterns.

        Args:
            patterns: List of ignore patterns

        Returns:
            A pathspec object
        """
        return PathSpec.from_lines("gitwildmatch", patterns)

    @staticmethod
    def load_patterns(ignore_file: Path, combine: bool) -> list[str]:
        """Load patterns from a specific ignore file.

        Args:
            ignore_file: Path to the ignore file
        """
        if not ignore_file.exists():
            return []
        with suppress(FileNotFoundError):
            lines: list[str] = ignore_file.read_text().splitlines()
            patterns: list[str] = [
                line.strip()
                for line in lines
                if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("!")
            ]
            if combine:
                patterns.extend(IGNORE_PATTERNS)
            return patterns or IGNORE_PATTERNS
        return []

    def inject_pattern(self, pattern: str) -> None:
        """Inject a single pattern into the existing spec.

        Args:
            pattern: The pattern to inject
        """
        if not pattern or pattern in IGNORE_PATTERNS:
            return

        self.patterns.append(pattern)
        self.spec = self._create_spec(self.patterns)
        self.logger.verbose(f"Injected new pattern '{pattern}' into the ignore spec.")

    def inject_patterns(self, patterns: list[str]) -> None:
        """Inject additional patterns into the existing spec.

        Args:
            patterns: List of additional patterns to inject
        """
        if not patterns:
            return

        new_patterns: list[str] = [p for p in patterns if p not in self.patterns]
        self.patterns = [*new_patterns, *self.patterns]
        self.spec = self._create_spec(self.patterns)
        self.logger.verbose(f"Injected {len(new_patterns)} new patterns into the ignore spec.")

    def should_ignore(self, path: Path | str) -> bool:
        """Check if a given path should be ignored based on the ignore patterns.

        Args:
            path (Path): The path to check
        Returns:
            bool: True if the path should be ignored, False otherwise
        """
        path = Path(path).expanduser()
        if path.is_dir() and not str(path).endswith("/"):
            return self.spec.match_file(str(path) + "/")
        return self.spec.match_file(str(path))

    def ignore_print(self, path: Path | str, rel: bool = True) -> bool:
        """Print whether a given path is ignored based on the ignore patterns.

        Will print the path as relative to the current working directory if rel is True,
        which it is by default.

        Args:
            path (Path): The path to check
            rel (bool): Whether to print the path as relative to the current working directory

        Returns:
            bool: True if the path is ignored, False otherwise
        """
        path = Path(path).expanduser()
        if rel:
            path = path.relative_to(Path.cwd())

        return self.should_ignore(path)

    def add_patterns(self, patterns: list[str]) -> None:
        """Add additional ignore patterns to the existing spec.

        Args:
            patterns: List of additional patterns to add
        """
        new_patterns = []
        default_patterns: list[str] = IGNORE_PATTERNS.copy()
        if self.spec:
            for pattern in patterns:
                if pattern not in default_patterns:
                    new_patterns.append(pattern)
            self.spec = PathSpec(new_patterns + default_patterns)


class IgnoreDirectoryHandler(IgnoreHandler):
    """Handles the logic for ignoring files and directories based on .gitignore-style rules."""

    def __init__(
        self,
        directory_to_search: Path | str,
        ignore_file: Path | None = None,
        rel: bool = True,
        scan: bool = False,
    ) -> None:
        """Initialize the IgnoreDirectoryHandler with a directory to search and an optional ignore file."""
        super().__init__(ignore_file)
        self.directory_to_search: Path = Path(directory_to_search).resolve()
        self.files = IgnoreContainer()
        self.rel: bool = rel
        if scan:
            self.ignore_report_full_codebase()

    @staticmethod
    def _scan_directory(directory: Path | str, spec: PathSpec) -> tuple[list[Path], list[Path]]:
        """Scan a directory and separate files and directories into ignored and non-ignored lists.

        Args:
            directory: The directory to scan

        Returns:
            Tuple of (non_ignored_files, ignored_files) as relative Path objects
        """
        directory = Path(directory)
        all_paths: list[str] = []

        for root, _, files in os.walk(directory):
            root_path = Path(root)
            rel_root: Path = root_path.relative_to(directory)

            if str(rel_root) == ".":
                rel_root = Path("")
            else:
                dir_path: str = str(rel_root) + "/"
                all_paths.append(dir_path)

            for file in files:
                rel_path: Path = rel_root / file
                all_paths.append(str(rel_path))

        ignored_status: list[bool] = [spec.match_file(f) for f in all_paths]
        non_ignored_paths: list[str] = [f for f, ignored in zip(all_paths, ignored_status, strict=False) if not ignored]
        ignored_paths: list[str] = [f for f, ignored in zip(all_paths, ignored_status, strict=False) if ignored]
        return [Path(directory / p) for p in non_ignored_paths], [Path(directory / p) for p in ignored_paths]

    @property
    def ignored_files_count(self) -> int:
        """Get the count of ignored files.

        Returns:
            int: The number of ignored files
        """
        return self.files.ignored_count

    @property
    def non_ignored_files_count(self) -> int:
        """Get the count of non-ignored files.

        Returns:
            int: The number of non-ignored files
        """
        return self.files.non_ignored_count

    def ignore_report_full_codebase(self) -> None:
        """Generate a report of ignored and non-ignored files in the directory.

        Returns:
            Tuple of (non_ignored_files, ignored_files) as Path objects
        """
        self.files.store_result(self._scan_directory(self.directory_to_search, self.spec))

    def _print(self, files: list[Path], rel: bool = True, color: str = "white") -> None:
        """Print the contents of a data structure (list of paths) to the console.

        Args:
            files: The data structure to print
            rel: Whether to print the paths as relative to the current working directory
        """
        try:
            for path in files:
                p = Path(path)
                if rel:
                    p: Path = p.relative_to(Path.cwd())
                self.logger.print(p, style=color) if self.logger.level == LogLevel.VERBOSE else None
        except KeyboardInterrupt:
            self.logger.verbose("KeyboardInterrupt detected. Stopping printing.")

    def _print_files(self, chosen: Literal["ignored", "non-ignored"]) -> None:
        """Print the non-ignored files in the directory."""
        files: list[Path] = self.files.non_ignored if chosen == "non-ignored" else self.files.ignored
        if len(files) == 0:
            self.logger.verbose("No non-ignored files found.")
            return
        if len(files) > IGNORE_COUNT:
            if Confirm.ask(
                f"There are a lot of {chosen} files. Do you want to print them all?",
                choices=["y", "n"],
                show_choices=True,
                default=False,
            ):
                self._print(files, self.rel)
        else:
            self._print(files, self.rel)

    def print_report(self, what_to_print: str):
        """Print the report of ignored or non-ignored files or both

        Args:
            what_to_print: "ignored", "non_ignored", or "both"
        """
        match what_to_print:
            case "ignored" | "non-ignored":
                self._print_files(what_to_print)
            case "both":
                self._print_files("ignored")
                self._print_files("non-ignored")
            case _:
                raise ValueError(f"Invalid option: {what_to_print}. Use 'ignored', 'non-ignored', or 'both'.")
