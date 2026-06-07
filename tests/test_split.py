"""Tests for WidPathResolver._split_wid - WID chunking."""

from widpath import WidPathResolver


def test_standard_uuid_32_chars_size2():
    r = WidPathResolver()
    parts = r._split_wid("4a3f9c2b1e0d5678abcd1234567890ab")
    assert len(parts) == 16
    assert parts[0] == "4a"
    assert parts[1] == "3f"
    assert parts[-1] == "ab"


def test_size_1_each_char_is_segment():
    r = WidPathResolver(size=1)
    parts = r._split_wid("4a3f")
    assert parts == ["4", "a", "3", "f"]


def test_size_4_four_chars_per_segment():
    r = WidPathResolver(size=4)
    parts = r._split_wid("4a3f9c2b")
    assert parts == ["4a3f", "9c2b"]


def test_odd_length_last_chunk_shorter():
    """If len(wid) % size != 0, last chunk is the remainder."""
    r = WidPathResolver(size=2)
    parts = r._split_wid("4a3f9")   # 5 chars
    assert parts == ["4a", "3f", "9"]


def test_single_segment_wid():
    r = WidPathResolver(size=2)
    parts = r._split_wid("4a")
    assert parts == ["4a"]


def test_empty_string_returns_empty_list():
    r = WidPathResolver(size=4)
    assert r._split_wid("") == []
