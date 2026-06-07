"""Integration tests for get_file_path and locate using real temp directories."""


import pytest

from widpath import locate

WID = "4a3f9c2b1e0d5678abcd1234567890ab"


# ---------------------------------------------------------------------------
# locate() - linear-scan algorithm
# ---------------------------------------------------------------------------

class TestLocate:
    def test_empty_dir_returns_shallowest(self, tmp_path):
        result = locate(tmp_path, WID)
        assert result == tmp_path / "4a.json"

    def test_subdir_l1_exists(self, tmp_path):
        (tmp_path / "4a").mkdir()
        result = locate(tmp_path, WID)
        assert result == tmp_path / "4a" / "3f.json"

    def test_subdir_l2_exists(self, tmp_path):
        (tmp_path / "4a" / "3f").mkdir(parents=True)
        result = locate(tmp_path, WID)
        assert result == tmp_path / "4a" / "3f" / "9c.json"

    def test_file_does_not_affect_traversal(self, tmp_path):
        """locate() only check is_dir(), not file existence."""
        (tmp_path / "4a.json").write_text("{}")
        # "4a" is a file, not a directory, so it stops at level 0
        result = locate(tmp_path, WID)
        assert result == tmp_path / "4a.json"

    def test_custom_size(self, tmp_path):
        result = locate(tmp_path, WID, size=4)
        assert result == tmp_path / "4a3f.json"

    def test_full_depth_dirs(self, tmp_path):
        """When every segment has a directory, result is inside the deepest dir."""
        deep = tmp_path
        segments = [WID[i:i+2] for i in range(0, len(WID), 2)]
        for seg in segments:
            deep = deep / seg
            deep.mkdir()
        result = locate(tmp_path, WID)
        # All dirs exist -> falls through -> last segment repeated as filename
        assert result == deep / f"{segments[-1]}.json"


# ---------------------------------------------------------------------------
# WidPathResolver.resolve() - binary-search algorithm
# ---------------------------------------------------------------------------

class TestResolve:
    def test_empty_dir_returns_shallowest(self, tmp_path, resolver):
        result = resolver.resolve(WID, tmp_path)
        assert result == tmp_path / "4a.json"

    def test_existing_shallow_file_returned(self, tmp_path, resolver):
        (tmp_path / "4a.json").write_text("{}")
        result = resolver.resolve(WID, tmp_path)
        assert result == tmp_path / "4a.json"

    def test_subdir_exists_returns_next_level(self, tmp_path, resolver):
        (tmp_path / "4a").mkdir()
        result = resolver.resolve(WID, tmp_path)
        assert result == tmp_path / "4a" / "3f.json"

    def test_deep_subdir_chain(self, tmp_path, resolver):
        (tmp_path / "4a" / "3f" / "9c").mkdir(parents=True)
        result = resolver.resolve(WID, tmp_path)
        assert result == tmp_path / "4a" / "3f" / "9c" / "2b.json"

    def test_existing_deep_file(self, tmp_path, resolver):
        (tmp_path / "4a" / "3f").mkdir(parents=True)
        deep_file = tmp_path / "4a" / "3f" / "9c.json"
        deep_file.write_text("{}")
        result = resolver.resolve(WID, tmp_path)
        assert result == deep_file

    def test_base_dir_not_exist_raises(self, tmp_path, resolver):
        with pytest.raises(FileNotFoundError, match="base_dir"):
            resolver.resolve(WID, tmp_path / "nonexistent")

    def test_result_is_always_json(self, tmp_path, resolver):
        result = resolver.resolve(WID, tmp_path)
        assert result.suffix == ".json"

    def test_result_under_base_dir(self, tmp_path, resolver):
        result = resolver.resolve(WID, tmp_path)
        assert str(result).startswith(str(tmp_path))


# ---------------------------------------------------------------------------
# Consistency: locate and get_file_path agree on the same filesystem state
# ---------------------------------------------------------------------------

class TestAlgorithmConsistency:
    @pytest.mark.parametrize("depth", [0, 1, 2, 3])
    def test_locate_and_get_file_path_agree(self, tmp_path, resolver, depth):
        """Both algorithms should return the same path for any given directory state."""
        segments = [WID[i:i+2] for i in range(0, len(WID), 2)]
        # Create `depth` levels of directories
        current = tmp_path
        for seg in segments[:depth]:
            current = current / seg
            current.mkdir()

        locate_result = locate(tmp_path, WID)
        bsearch_result = resolver.resolve(WID, tmp_path)
        assert locate_result == bsearch_result
