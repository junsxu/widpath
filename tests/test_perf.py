"""Performance benchmarks - not run in regular CI, invoke with pytest -m perf."""

import time
from pathlib import Path

import pytest

from widpath import WidPathResolver, locate

WID = "4a3f9c2b1e0d5678abcd1234567890ab"
ITERATIONS = 100_000


@pytest.mark.perf
def test_path_at_level_throughput():
    r = WidPathResolver()
    start = time.perf_counter()
    for _ in range(ITERATIONS):
        r.path_at_level(WID, 0)
    elapsed = time.perf_counter() - start
    assert elapsed < 1.0, f"100K calls took {elapsed:.2f}s (> 1s threshold)"


@pytest.mark.perf
def test_locat_empty_dir_throughput(tmp_path):
    start = time.perf_counter()
    for _ in range(ITERATIONS):
        locate(tmp_path, WID)
    elapsed = time.perf_counter() - start
    assert elapsed < 2.0, f"100k locate() calls took {elapsed:.2f}s (> 2s threshold)"


@pytest.mark.perf
def test_binary_search_stat_count(tmp_path):
    """Binary search visits at most log2(16)+1 = 5 levels for a 16-level WID."""
    r = WidPathResolver()
    stat_calls: list[Path] = []
    original_exists = Path.exists

    def counting_exists(self: Path) -> bool:
        stat_calls.append(self)
        return original_exists(self)
    
    import unittest.mock as mock

    with mock.patch.object(Path, "exists", counting_exists):
        r.resolve(WID, tmp_path)
    
    assert len(stat_calls) <= 6, (
        f"Binary search made {len(stat_calls)} stat calls (expected ≤ 6)"
    )
