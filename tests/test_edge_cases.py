"""Edge-case and cross-platform tests."""

from pathlib import Path

import pytest

from widpath import WidPathResolver, locate


class TestSingleSegment:
    """WID length equals size -> max_level == 0, only one possible path."""

    def test_max_level_is_zero(self):
        r = WidPathResolver(size=2)
        assert r.max_level("4a") == 0

    def test_path_at_level_single(self):
        r = WidPathResolver(size=2)
        assert r.path_at_level("4a", 0) == Path("4a.json")

    def test_resolve_single(self, tmp_path):
        r = WidPathResolver(size=2)
        result = r.resolve("4a", tmp_path)
        assert result == tmp_path / "4a.json"

    def test_locate_single(self, tmp_path):
        result = locate(tmp_path, "4a", size=2)
        assert result == tmp_path / "4a.json"


class TestUUIDWithDashes:
    """UUIDs must have dashes stripped before being passed to widpath."""

    def test_uuid_with_dashes_splits_incorrectly(self):
        r = WidPathResolver(size=2)
        # dashes should be stripped by the caller
        raw = "4a3f9c2b-1e0d-5678-abcd-1234567890ab"
        stripped = raw.replace("-", "")
        parts_raw = r._split_wid(raw)
        parts_stripped = r._split_wid(stripped)
        # raw contains '-' so chunks differ
        assert parts_raw != parts_stripped

    def test_stripped_uuid_has_32_chars(self):
        raw = "4a3f9c2b-1e0d-5678-abcd-1234567890ab"
        assert len(raw.replace("-", "")) == 32


class TestPathSeparators:
    """Paths produced by widpath must be valid on the current OS."""

    def test_path_at_level_uses_pathlib(self):
        r = WidPathResolver()
        p = r.path_at_level("4a3f9c2b1e0d5678abcd1234567890ab", 2)
        assert isinstance(p, Path)
        # pathlib uses OS-native separator when converting to str
        assert str(p) == str(Path("4a") / "3f" / "9c.json")

    def test_locate_result_is_path(self, tmp_path):
        result = locate(tmp_path, "4a3f9c2b1e0d5678abcd1234567890ab")
        assert isinstance(result, Path)

    def test_resolve_result_is_absolute_under_tmp(self, tmp_path):
        r = WidPathResolver()
        result = r.resolve("4a3f9c2b1e0d5678abcd1234567890ab", tmp_path)
        assert result.is_absolute()


class TestCustomSize:
    def test_size_1_locate(self, tmp_path):
        result = locate(tmp_path, "4a3f", size=1)
        assert result == tmp_path / "4.json"

    def test_size_4_resolver(self, tmp_path):
        r = WidPathResolver(size=4)
        result = r.resolve("4a3f9c2b1e0d5678abcd1234567890ab", tmp_path)
        assert result == tmp_path / "4a3f.json"

    def test_size_8_resolver(self, tmp_path):
        r = WidPathResolver(size=8)
        result = r.resolve("4a3f9c2b1e0d5678abcd1234567890ab", tmp_path)
        assert result == tmp_path / "4a3f9c2b.json"


class TestBaseDir:
    def test_nonexistent_base_dir_raises_file_not_found(self, tmp_path):
        r = WidPathResolver()
        with pytest.raises(FileNotFoundError):
            r.resolve("4a3f9c2b1e0d5678abcd1234567890ab", tmp_path / "missing")

    def test_nested_base_dir(self, tmp_path):
        base = tmp_path / "data" / "nodes"
        base.mkdir(parents=True)
        r = WidPathResolver()
        result = r.resolve("4a3f9c2b1e0d5678abcd1234567890ab", base)
        assert result == base / "4a.json"
