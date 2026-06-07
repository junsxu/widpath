# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Changed
- **Breaking:** Renamed `WidPathResolver` methods to be more Pythonic and precise:
  - `get_file_path(wid, base_dir)` -> `resolve(wid, base_dir)` - aligns with the class name *Resolver*.
  - `get_hierarchical_json(wid, level)` -> `path_at_level(wid, level)` - describes what the method returns rather than the output format.
  - `get_max_level(wid)` -> `max_level(wid)` - drops the un-Pythonic `get_` prefix from a pure-computation method.
  - `get_candidate_paths(wid, base_dir)` -> `candidate_paths(wid, base_dir)` - same rationale as above.

---

## [0.2.0] - 2026-06-03

### Added
- `locate(base_dir, wid, size=2)` - module-level functional interface implementing
  the canonical O(depth) linear-scan algorithm from the widpath specification.
- `WidPathResolver.get_candidate_paths(wid, base_dir)` - returns all candidate paths
  from shallowest to deepest; useful for debugging and tooling.
- `WidPathResolver.__init__.py` now exports `__version__ = "0.2.0"`.
- Full test suite: `test_split`, `test_levels`, `test_locate`, `test_edge_cases`,
  `test_perf` - coverage ≥ 95 %.
- GitHub Actions CI workflow (Python 3.9-3.13 matrix, ruff, mypy).
- GitHub Actions publish workflow (OIDC Trusted Publishing -> PyPI on Release).
- Bilingual README (EN + CN).
- `pyproject.toml` replaces legacy `setup.py`.

### Changed
- **Breaking:** `WidPathResolver.get_file_path(wid)` now requires a mandatory
  `base_dir: Path` argument. Previously the method used the process CWD
  implicitly, which was unsafe in library code.
- `WidPathResolver.get_hierarchical_json` now uses `pathlib` path composition
  (`Path(*parts).with_suffix(".json")`) instead of string join with a
  configurable `separator`.
- `WidPathResolver.__init__` no longer accepts a `separator` parameter
  (removed - `pathlib` handles OS-native separators automatically).

### Fixed
- `get_file_path` now raises `FileNotFoundError` when `base_dir` does not exist,
  instead of silently returning an invalid path.
- `get_max_level == 0` edge case (WID length equals `size`) is now handled
  explicitly with an early return.

---

## [0.1.1] - 2025-10-08

### Fixed
- Minor metadata corrections in package distribution.

---

## [0.1.0] - 2025-09-21

### Added
- Initial release.
- `WidPathResolver` with `get_file_path`, `get_hierarchical_json`, `get_max_level`.

[Unreleased]: https://github.com/junsxu/widpath/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/junsxu/widpath/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/junsxu/widpath/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/junsxu/widpath/releases/tag/v0.1.0
