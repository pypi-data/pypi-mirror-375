from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, TypeAlias

from rich.console import Console

from .profile import Profile
from .storage import JsonStorage, StorageBackend
from .utils.ignore_utils import IgnoreManager
from .utils.path_utils import make_absolute, make_relative, normalize_paths

# Type aliases for clarity
FilePath: TypeAlias = str
Pattern: TypeAlias = str
FileStats: TypeAlias = Dict[str, int]

console = Console()


class ContextManager:
    """
    Manages the current "context" of files and directories.
    Keeps track of files and provides methods to manipulate them.

    The ContextManager uses a pluggable storage backend for persisting state.
    By default, it uses JsonStorage which maintains backward compatibility
    with the original file-based storage format. The storage abstraction
    allows for easy extension to support different storage mechanisms
    (e.g., profiles, cloud storage) without modifying core functionality.

    Args:
        storage: Optional storage backend implementation. If not provided,
                defaults to JsonStorage using the .contextr directory.
    """

    def __init__(self, storage: Optional[StorageBackend] = None) -> None:
        self.files: Set[FilePath] = set()
        self.watched_patterns: Set[Pattern] = set()
        self.base_dir: Path = Path.cwd()
        self.state_dir: Path = self.base_dir / ".contextr"
        self.state_file: Path = self.state_dir / "state.json"
        self.storage: StorageBackend = storage or JsonStorage(self.state_dir)
        self.ignore_manager: IgnoreManager = IgnoreManager(self.base_dir)
        self.current_profile_name: Optional[str] = None
        self.is_dirty: bool = False
        self._initial_state: Optional[Dict[str, List[str]]] = None
        self._load_state()

    def add_ignore_patterns(self, patterns: List[Pattern]) -> Tuple[int, int]:
        """
        Add new patterns to .ignore and update current context (single refresh).

        Args:
            patterns: Patterns to add (glob-style)

        Returns:
            Tuple[int, int]: (Number of files removed, Number of directories cleaned)
        """
        for p in patterns:
            self.ignore_manager.add_pattern(p)
        before = set(self.files)
        self.refresh_watched()
        removed = before - self.files
        cleaned_dirs = {str(Path(p).parent) for p in removed}
        # Prefer accurate removal count from diff
        return len(removed), len(cleaned_dirs)

    # Back-compat single-pattern entry point
    def add_ignore_pattern(self, pattern: Pattern) -> Tuple[int, int]:
        return self.add_ignore_patterns([pattern])

    def remove_ignore_patterns(self, patterns: List[Pattern]) -> int:
        """
        Remove patterns from .ignore file (single refresh).

        Args:
            patterns: Patterns to remove

        Returns:
            int: Count of patterns removed
        """
        removed = 0
        for p in patterns:
            if self.ignore_manager.remove_pattern(p):
                removed += 1
        # Keep context consistent with watch patterns after ignore changes
        self.refresh_watched()
        return removed

    # Back-compat single-pattern removal
    def remove_ignore_pattern(self, pattern: Pattern) -> bool:
        return self.remove_ignore_patterns([pattern]) > 0

    def list_ignore_patterns(self) -> List[Pattern]:
        """
        Get list of current ignore patterns.

        Returns:
            List[Pattern]: List of glob-style ignore patterns
        """
        return self.ignore_manager.list_patterns()

    def sync_gitignore(self) -> Tuple[int, List[str]]:
        """
        Sync patterns from .gitignore to .ignore file.

        Returns:
            Tuple[int, List[str]]: (Number of new patterns added, List of new patterns)
        """
        gitignore_path = self.base_dir / ".gitignore"
        if not gitignore_path.exists():
            return 0, []

        # Read .gitignore patterns and trim inline comments (pattern " # comment")
        gitignore_patterns: List[Pattern] = []
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if not s or s.startswith("#"):
                    continue
                # Remove simple inline comments (not escaped)
                if " #" in s:
                    s = s.split(" #", 1)[0].rstrip()
                gitignore_patterns.append(s)

        existing = set(self.ignore_manager.list_patterns())  # includes '!'-prefixed
        new_patterns_list = [p for p in gitignore_patterns if p not in existing]

        for pattern in new_patterns_list:
            self.ignore_manager.add_pattern(pattern)

        return len(new_patterns_list), new_patterns_list

    def initialize(self) -> Tuple[bool, bool]:
        """
        Initialize .contextr directory (no longer updates .gitignore).

        Returns:
            Tuple[bool, bool]: (Created .contextr, Updated .gitignore [always False])
        """
        # TODO: Consider returning a dataclass instead of tuple for clarity
        created_dir = False
        updated_gitignore = False

        # Create .contextr directory if it doesn't exist
        if not self.state_dir.exists():
            self.state_dir.mkdir(parents=True)
            created_dir = True

        return created_dir, updated_gitignore

    def _load_state(self) -> None:
        """Load state (files and watched patterns) from storage."""
        try:
            data = self.storage.load("state")
            if data:
                # Validate and load files
                self.files = set(
                    make_absolute(p, self.base_dir) for p in data.get("files", [])
                )
                # Validate and load watched patterns
                self.watched_patterns = set(data.get("watched_patterns", []))
                # Load profile tracking state
                self.current_profile_name = data.get("current_profile")
                # Capture initial state for dirty checking
                self._capture_initial_state()
        except IOError as e:
            console.print(f"[red]Error loading state: {e}[/red]")

    def _save_state(self) -> None:
        """Save current state (files and watched patterns) to storage."""
        try:
            data = {
                "files": [make_relative(p, self.base_dir) for p in sorted(self.files)],
                "watched_patterns": sorted(
                    self.watched_patterns
                ),  # Save watched patterns
                "current_profile": self.current_profile_name,
            }
            self.storage.save("state", data)
            # Check if state has changed
            self._check_dirty_state()
        except IOError as e:
            console.print(f"[red]Error saving state: {e}[/red]")

    def _add_files(self, patterns: List[Pattern], persist: bool = True) -> int:
        """Internal method to add files, respecting ignore patterns."""
        abs_paths = normalize_paths(patterns, self.base_dir, self.ignore_manager)
        if not abs_paths:
            return 0

        new_files_count = 0
        for path_str in abs_paths:
            p = Path(path_str)
            if p.is_file() and not self.ignore_manager.should_ignore(path_str):
                if path_str not in self.files:
                    new_files_count += 1
                self.files.add(path_str)
            elif p.is_dir():
                # Add all files within the directory that aren't ignored
                for file_path in p.rglob("*"):
                    if file_path.is_file():
                        file_abs = str(file_path.resolve())
                        if not self.ignore_manager.should_ignore(file_abs):
                            if file_abs not in self.files:
                                new_files_count += 1
                            self.files.add(file_abs)

        if persist:
            self._save_state()
        return new_files_count

    def _remove_files(self, patterns: List[Pattern]) -> int:
        """
        Internal method to remove files or directories from the context.
        If a directory is removed, all files under it are also removed.

        Args:
            patterns: List of file/directory patterns to remove

        Returns:
            int: Number of files removed
        """
        abs_paths = normalize_paths(patterns, self.base_dir)
        if not abs_paths:
            return 0

        files_to_remove: Set[FilePath] = set()
        for path_str in abs_paths:
            p = Path(path_str)
            if p.is_file():
                if path_str in self.files:
                    files_to_remove.add(path_str)
            elif p.is_dir():
                # Remove all files under that directory
                for file_path in p.rglob("*"):
                    fp_str = str(file_path.resolve())
                    if fp_str in self.files:
                        files_to_remove.add(fp_str)

        removed_count = len(files_to_remove)
        self.files -= files_to_remove
        self._save_state()
        return removed_count

    def clear_context(self) -> None:
        """
        Clear all files from context.

        Side Effects:
            - Removes all files from current context
            - Saves empty state to disk
        """
        self.files.clear()
        self._save_state()

    def clear(self, preserve_ignores: bool = True) -> None:
        """
        Clear context data including files and watched patterns.
        By default, **preserves** repo-level ignore rules.

        Side Effects:
            - Removes all files from current context
            - Clears watched patterns
            - Optionally clears ignore patterns
            - Saves empty state to disk
        """
        self.files.clear()
        self.watched_patterns.clear()
        if not preserve_ignores:
            try:
                self.ignore_manager.clear_patterns()
            except (PermissionError, FileNotFoundError, OSError):
                pass
        self._save_state()

    def search_files(self, keyword: str) -> List[FilePath]:
        """
        Search for files in the context containing the given keyword in their path.

        Args:
            keyword: Search term

        Returns:
            List[str]: List of matching file paths (relative to base_dir)
        """
        return [
            make_relative(f, self.base_dir)
            for f in self.files
            if keyword.lower() in f.lower()
        ]

    def get_file_paths(self, relative: bool = True) -> List[FilePath]:
        """
        Get all file paths in the context.

        Args:
            relative: Whether to return relative paths

        Returns:
            List[str]: List of file paths
        """
        if relative:
            return [make_relative(f, self.base_dir) for f in sorted(self.files)]
        return sorted(self.files)

    def unwatch_paths(self, patterns: List[Pattern]) -> Tuple[int, int]:
        """
        Remove paths from watch list and automatically remove associated files.

        Args:
            patterns: List of patterns to stop watching

        Returns:
            Tuple[int, int]: (Number of patterns removed, Number of files removed)
        """
        removed_patterns: Set[Pattern] = set()
        files_before = len(self.files)

        # Remove patterns
        for pattern in patterns:
            if pattern in self.watched_patterns:
                removed_patterns.add(pattern)

        self.watched_patterns -= removed_patterns

        # Auto-sync: Refresh to keep only files from remaining patterns
        self.refresh_files()

        files_removed = files_before - len(self.files)

        self._save_state()

        return len(removed_patterns), files_removed

    def watch_paths(self, patterns: List[Pattern]) -> Tuple[int, int]:
        """
        Add paths to watch list and perform initial file addition.
        Filters out ignored patterns before adding to watch list.

        Args:
            patterns: List of file/directory patterns to watch

        Returns:
            Tuple[int, int]: (Number of new patterns, Number of files added)
        """
        # Always record what the user asked to watch; filtering happens per-file
        new_patterns: Set[Pattern] = set(patterns) - self.watched_patterns
        self.watched_patterns.update(new_patterns)

        # Initial add (per-file ignore rules apply in _add_files)
        added_count = self._add_files(patterns)

        self._save_state()
        return len(new_patterns), added_count

    def refresh_watched(self) -> FileStats:
        """
        Refresh all watched paths to detect changes.
        Only includes non-ignored files in the refresh.

        Returns:
            Dict[str, int]: Statistics about changes (added, removed files)
        """
        stats: FileStats = {"added": 0, "removed": 0}
        old_files: Set[FilePath] = self.files.copy()

        # Clear files that came from watched patterns
        self.files.clear()

        # Re-add all files from watched patterns; persist once at end
        for pattern in self.watched_patterns:
            added = self._add_files([pattern], persist=False)
            stats["added"] += added

        # Count removed files
        stats["removed"] = len(old_files - self.files)
        # Single save for the whole refresh
        self._save_state()

        return stats

    def list_watched(self) -> List[Pattern]:
        """
        Get list of currently watched patterns, excluding those that would be ignored.

        Returns:
            List[Pattern]: Sorted list of valid watched patterns
        """
        # Show everything the user asked to watch (even if currently yielding 0 files)
        return sorted(self.watched_patterns)

    def save_state_as(self, state_name: str) -> bool:
        """
        Save current state to a named file in the states directory.

        Args:
            state_name: Name of the state to save

        Returns:
            bool: True if save was successful
        """
        # Ensure state name is valid
        state_name = state_name.replace(" ", "_")
        # Remove .json extension if present for key
        if state_name.endswith(".json"):
            state_name = state_name[:-5]

        key = f"states/{state_name}"

        try:
            data = {
                "files": [make_relative(p, self.base_dir) for p in sorted(self.files)],
                "watched_patterns": sorted(self.watched_patterns),
                "ignore_patterns": sorted(
                    self.ignore_manager.get_normal_patterns_set()
                ),
                "negation_patterns": sorted(
                    self.ignore_manager.get_negation_patterns_set()
                ),
            }
            self.storage.save(key, data)
            return True
        except IOError as e:
            console.print(f"[red]Error saving state '{state_name}': {e}[/red]")
            return False

    def load_state(self, state_name: str) -> bool:
        """
        Load a previously saved state.

        Args:
            state_name: Name of the state to load

        Returns:
            bool: True if load was successful
        """
        # Remove .json extension if present for key
        if state_name.endswith(".json"):
            state_name = state_name[:-5]

        key = f"states/{state_name}"

        try:
            data = self.storage.load(key)
            if not data:
                console.print(f"[red]State file not found: {state_name}[/red]")
                return False

            # Load files with validation
            self.files = set(
                make_absolute(p, self.base_dir) for p in data.get("files", [])
            )

            # Load watched patterns with validation
            self.watched_patterns = set(data.get("watched_patterns", []))

            # Load ignore patterns with validation (deterministic order)
            normals = set(data.get("ignore_patterns", []))
            negs = set(data.get("negation_patterns", []))
            self.ignore_manager.set_patterns(normals, negs)

            self._save_state()  # Save as current state
            return True
        except IOError as e:
            console.print(f"[red]Error loading state '{state_name}': {e}[/red]")
            return False

    def list_saved_states(self) -> List[str]:
        """
        Get list of all saved states.

        Returns:
            List[str]: Names of saved states
        """
        # Get all keys with states/ prefix and remove the prefix
        states = self.storage.list_keys("states/")
        return [state.replace("states/", "") for state in states]

    def delete_state(self, state_name: str) -> bool:
        """
        Delete a saved state file.

        Args:
            state_name: Name of the state to delete

        Returns:
            bool: True if deletion was successful
        """
        # Remove .json extension if present for key
        if state_name.endswith(".json"):
            state_name = state_name[:-5]

        key = f"states/{state_name}"

        try:
            if not self.storage.exists(key):
                console.print(f"[red]State file not found: {state_name}[/red]")
                return False
            return self.storage.delete(key)
        except IOError as e:
            console.print(f"[red]Error deleting state '{state_name}': {e}[/red]")
            return False

    def apply_profile(self, profile: Profile, profile_name: str) -> None:
        """
        Replace current context with profile's watched patterns (branch-like checkout).
        Repo-level ignores are **not** modified.

        Args:
            profile: Profile object containing patterns to apply
            profile_name: Name of the profile being loaded

        Side Effects:
            - Clears current context (preserves ignores)
            - Applies profile patterns
            - Triggers automatic file refresh
            - Sets current profile name and resets dirty flag
        """
        self.clear(preserve_ignores=True)
        self.watched_patterns = set(profile.watched_patterns)
        self.current_profile_name = profile_name
        self.refresh_watched()
        self.reset_dirty_state()  # Reset dirty tracking after loading profile

    def refresh_files(self) -> int:
        """
        Refresh files based on current watched patterns.
        This is the primary sync mechanism that ensures files match watched patterns.

        Returns:
            int: Number of files added
        """
        # Keep API but delegate to the accurate stats method
        stats = self.refresh_watched()
        return stats["added"]

    def _capture_initial_state(self) -> None:
        """Capture the current state for dirty checking."""
        self._initial_state = {
            "watched_patterns": sorted(self.watched_patterns),
        }
        self.is_dirty = False

    def reset_dirty_state(self) -> None:
        """Public method to reset dirty state tracking."""
        self._capture_initial_state()

    def _check_dirty_state(self) -> None:
        """Check if current state differs from initial state."""
        if self._initial_state is None:
            self._capture_initial_state()
            return

        current_state = {"watched_patterns": sorted(self.watched_patterns)}
        self.is_dirty = current_state != self._initial_state
