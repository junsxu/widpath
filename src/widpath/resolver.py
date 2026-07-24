"""Core widpath resolver - maps WID strings to hierarchical file-system paths."""

from __future__ import annotations

from pathlib import Path
from typing import Optional


def locate(base_dir: Path, wid: str, size: int = 2) -> Path:
    """Locate the JSON file for *wid* by following existing directories.

    This is the canonical O(depth) algorithm from the widpath specification.
    Starting from *base_dir*, it greedily descends into any existing
    subdirectory named by the next WID segment, and stops at the first
    segment whose corresponding entry is not a directory.

    Args:
        base_dir: Root directory to search in.
        wid: Hex string with dashes already removed (e.g. ``"4a3f9c2b..."``).
        size: Number of hex characters per path segment. Defaults to ``2``.

    Returns:
        Path to the ``.json`` file (may or may not exist yet).

    Example:
        >>> from pathlib import Path
        >>> locate(Path("data/nodes"), "4a3f9c2b1e0d5678abcd1234567890ab")
        PosixPath('data/nodes/4a.json')     # when data/nodes/ is empty
    """
    segments = [wid[i : i + size] for i in range(0, len(wid), size)]
    current = base_dir
    for seg in segments:
        if (current / seg).is_dir():
            current = current / seg
        else:
            return current / f"{seg}.json"
    # All segments were directories - return file inside the deepest dir.
    return current / f"{segments[-1]}.json"


class WidPathResolver:
    """Resolves WID strings to hierarchical JSON file paths.

    A WID (World ID) is any fixed-length hex string such as a UUID4 with
    dashes stripped. The resolver maps it to a path like::

        base_dir/ab/cd/ef.json

    using the widpath specification: the WID is split into ``size``-character
    segments, and each segment becomes either a directory component or the
    final filename stem. Files are located with a binary-search strategy
    over depth levels, which limits I/O to O(log depth) <= O(4) stat calls
    for the default 16-level UUID layout.

    Args:
        size: Number of hex characters per path segment. Defaults to ``2```.

    Example:
        >>> resolver = WidPathResolver()
        >>> resolver.resolve("4a3f9c2b1e0d5678abcd1234567890ab", Path("data/nodes"))
        PosixPath('data/nodes/4a.json')
    """

    def __init__(self, size: int = 2) -> None:
        self.size = size

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _split_wid(self, wid: str) -> list[str]:
        """Split *wid* into fixed-size chunks.

        Args:
            wid: Hex string (dashes already removed).

        Returns:
            List of ``size``-character chunks. The last chunk may be shorter
            if ``len(wid)`` is not a multiple of ``size``.
        """
        return [wid[i : i + self.size] for i in range(0, len(wid), self.size)]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def max_level(self, wid: str) -> int:
        """Return the maximum valid level index for *wid*.

        At level ``0`` the path has one segment (e.g. ``ab.json``).
        At ``max_level`` the path has the maximum number of segments.

        Args:
            wid: Hex string (dashes already removed).

        Returns:
            ``len(wid) // size - 1``
        """
        return len(wid) // self.size - 1

    def path_at_level(self, wid: str, level: int) -> Path:
        """Build the relative path for *wid* at a given depth *level*.

        The returned path is **relative** (no base directory). Pass it to
        :meth:`resolve` or prepend a ``base_dir`` yourself.

        Args:
            wid: Hex string (dashes already removed).
            level: Depth level (``0`` = shallowest). Clamped to
                ``[0, max_level]``.

        Returns:
            A relative :class:`~pathlib.Path` ending in ``.json``.

        Example:
            >>> r = WidPathResolver()
            >>> r.path_at_level("4a3f9c2b", 0)
            PosixPath('4a.json')
            >>> r.path_at_level("4a3f9c2b", 1)
            PosixPath('4a/3f.json')
        """
        parts = self._split_wid(wid)
        top = self.max_level(wid)
        level = min(max(level, 0), top)
        # Build path: parts[0]/parts[1]/.../parts[level].json
        return Path(*parts[: level + 1]).with_suffix(".json")

    def candidate_paths(self, wid: str, base_dir: Path) -> list[Path]:
        """Return all candidate paths from shallowest to deepest.

        Useful for debugging or pre-generating the full path space for a WID.

        Args:
            wid: Hex string (dashes already removed).
            base_dir: Root directory to prepend to every path.

        Returns:
            List of :class:`~pathlib.Path` objects, index 0 = shallowest.
        """
        top = self.max_level(wid)
        return [
            base_dir / self.path_at_level(wid, lvl)
            for lvl in range(top + 1)
        ]

    def is_deepest_dir(
        self,
        wid: str,
        path: Path,
        base_dir: Optional[Path] = None,  # noqa: UP045
    ) -> bool:
        """Return whether *path* is the deepest directory for *wid*.

        The check is structural and does not require *path* to exist. When
        *base_dir* is supplied, absolute paths under it are converted to a
        relative path before comparison.

        Args:
            wid: Hex string (dashes already removed).
            path: Directory path to test. It may be relative to *base_dir* or
                absolute under *base_dir*.
            base_dir: Optional root directory used to relativize absolute
                *path* values.

        Returns:
            ``True`` if *path* is the parent directory of the deepest candidate
            JSON path for *wid*.
        """
        candidate = Path(path)
        if base_dir is not None:
            try:
                candidate = candidate.relative_to(base_dir)
            except ValueError:
                if candidate.is_absolute():
                    return False

        deepest_dir = self.path_at_level(wid, self.max_level(wid)).parent
        return candidate == deepest_dir

    def resolve(self, wid: str, base_dir: Path) -> Path:
        """Locate the JSON file for *wid* using a binary-search over depth levels.

        The search starts from the maximum depth and narrows down, returning
        the path of the shallowest existing file that could contain *wid*, or
        the target path at the shallowest level if nothing exists yet.

        Args:
            wid: Hex string (dashes already removed).
            base_dir: Root directory to search in. Must exist.

        Returns:
            :class:`~pathlib.Path` to the ``.json`` file (may not exist yet
            if the WID is new).

        Raises:
            FileNotFoundError: If *base_dir* does not exist.

        Example:
            >>> resolver = WidPathResolver()
            >>> resolver.resolve("4a3f9c2b1e0d5678abcd1234567890ab", Path("data/nodes"))
            PosixPath('data/nodes/4a.json')
        """
        if not base_dir.exists():
            raise FileNotFoundError(f"base_dir does not exist: {base_dir}")

        top = self.max_level(wid)

        # Fast path for single-segment WIDs.
        if top == 0:
            return base_dir / self.path_at_level(wid, 0)

        parts = self._split_wid(wid)

        # Binary search: find the deepest level L where prefix_dir(L) exists.
        # prefix_dir(L) = base_dir / parts[0] / ... / parts[L-1]
        # prefix_dir(0) = base_dir, which is already verified above.
        # Each probe costs exactly one stat call -> O(log max_level) total.
        lo = 0
        hi = top
        while lo < hi:
            mid = (lo + hi + 1) // 2    # bias upward to avoid infinite loop
            if (base_dir / Path(*parts[:mid])).exists():
                lo = mid
            else:
                hi = mid - 1

        return base_dir / self.path_at_level(wid, lo)
