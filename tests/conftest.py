"""Shared fixtures for widpath tests."""

import pytest

from widpath import WidPathResolver

WID_32 = "4a3f9c2b1e0d5678abcd1234567890ab"    # 32 hex chars -> 16 segments at size=2


@pytest.fixture
def resolver() -> WidPathResolver:
    """Default resolver with size=2."""
    return WidPathResolver()


@pytest.fixture
def wid() -> str:
    """A standard 32-char UUID4 (dashes removed)."""
    return WID_32
