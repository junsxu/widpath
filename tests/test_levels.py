"""Tests for get_max_level and get_hierarchical_json."""

from pathlib import Path

from widpath import WidPathResolver


class TestMaxLevel:
    def test_32_char_wid_size2(self):
        assert WidPathResolver().max_level("4a3f9c2b1e0d5678abcd1234567890ab") == 15

    def test_single_segment_wid(self):
        # "4a" -> 2 chars / 2 = 1 segment -> max_level = 0
        assert WidPathResolver().max_level("4a") == 0

    def test_size_4(self):
        # "4a3f9c2b" -> 8 chars / 4 = 2 segments -> max_level = 1
        assert WidPathResolver(size=4).max_level("4a3f9c2b") == 1

    def test_size_1(self):
        # "4a3f" -> 4 chars / 1 = 4 segments -> max_level = 3
        assert WidPathResolver(size=1).max_level("4a3f") == 3


class TestPathAtLevel:
    WID = "4a3f9c2b1e0d5678abcd1234567890ab"

    def test_level_0_returns_single_segment(self):
        r = WidPathResolver()
        assert r.path_at_level(self.WID, 0) == Path("4a.json")

    def test_level_1_returns_two_segments(self):
        r = WidPathResolver()
        assert r.path_at_level(self.WID, 1) == Path("4a/3f.json")

    def test_level_max_returns_full_path(self):
        r = WidPathResolver()
        expected = Path("4a/3f/9c/2b/1e/0d/56/78/ab/cd/12/34/56/78/90/ab.json")
        assert r.path_at_level(self.WID, 15) == expected

    def test_level_above_max_is_clamped(self):
        r = WidPathResolver()
        assert r.path_at_level(self.WID, 100) == r.path_at_level(self.WID, 15)

    def test_level_below_0_is_clamped(self):
        r = WidPathResolver()
        assert r.path_at_level(self.WID, -5) == Path("4a.json")

    def test_intermediate_level(self):
        r = WidPathResolver()
        assert r.path_at_level(self.WID, 2) == Path("4a/3f/9c.json")


class TestCandidatePaths:
    def test_returns_16_paths_for_32_char_wid(self, tmp_path):
        r = WidPathResolver()
        wid = "4a3f9c2b1e0d5678abcd1234567890ab"
        paths = r.candidate_paths(wid, tmp_path)
        assert len(paths) == 16

    def test_first_is_shallowest(self, tmp_path):
        r = WidPathResolver()
        wid = "4a3f9c2b1e0d5678abcd1234567890ab"
        paths = r.candidate_paths(wid, tmp_path)
        assert paths[0] == tmp_path / "4a.json"

    def test_last_is_deepest(self, tmp_path):
        r = WidPathResolver()
        wid = "4a3f9c2b1e0d5678abcd1234567890ab"
        paths = r.candidate_paths(wid, tmp_path)
        assert paths[-1] == tmp_path / "4a/3f/9c/2b/1e/0d/56/78/ab/cd/12/34/56/78/90/ab.json"

    def test_all_paths_under_base_dir(self, tmp_path):
        r = WidPathResolver()
        wid = "4a3f9c2b1e0d5678abcd1234567890ab"
        for p in r.candidate_paths(wid, tmp_path):
            assert str(p).startswith(str(tmp_path))
