# widpath

[![CI](https://github.com/junsxu/widpath/actions/workflows/ci.yml/badge.svg)](https://github.com/junsxu/widpath/actions/workflows/ci/yml)
[![PyPI version](https://badge.fury.io/py/widpath.svg)](https://pypi.org/project/widpath/)
[![Python](https://img.shields.io/pypi/pyversions/widpath)](https://pypi.org/project/widpath/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**widpath** maps WID strings (UUID4 or any fixed-length hex ID) to a hierarchical file-system path tree, keeping directory entry counts bounded while supporting O(1) point lookup - no database required.

---

## What problem does it solve?

Storing millions of UUID-keyed JSON files in a flat directory causes performance problems on every major OS (HFS+, ext4, NTFS all degrade beyong ~100 k entries per directory).

widpath borrows the idea from Git's objext store (`.git/objects/ab/cdef...`) and generalises it to **adaptive depth**: a single JSON file at a shallow level holds all WIDs that share the same prefix. When that file grows too large, the caller splits it into deeper sub-files - and widpath's `locate` / `resolve` find the right file in at most **16 stat calls** for a 32-char UUID.

```
data/nodes/
├── 8b.json             ← all WIDs starting with "8b" (few entries, stays shallow)
├── 4a/
|   ├── 3f.json         ← split: "4a3f..." WIDs moved here
|   └── b7.json         ← split: "4ab7..." WIDs moved here
└── ...
```

---

## Install

```bash
pip install widpath
```

Requires Python ≥ 3.9, no third-party dependencies.

---

## Quick start

```python
from pathlib import Path
from widpath import locate, WidPathResolver

base = Path("data/nodes")
wid = "4a3f9c2b1e0d5678abcd1234567890ab"    # UUID4 with dashes stripped

# ── Functional interface (canonical, O(depth) linear scan) ─────────────────
path = locate(base, wid)
# -> PosixPath('data/nodes/4a.json')  when base/ is empty

# ── OOP interface (binary-search variant, O(log depth)) ────────────────────
resolver = WidPathResolver()
path = resolver.srsolve(wid, base)
# same result
```

> **Note:** Strip UUID dashes before passing to widpath:
> `wid = uuid_str.replace("-", "")`

---

## API reference

### `locate(base_dir, wid, size=2) -> Path`

Canonical O(depth) algorithm. Greedily descends into existing subdirectories
named by successive WID segments, stopping at the first missing directory and
returning `<current>/<segment>.json`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_dir` | `Path` | - | Root storage directory |
| `wid` | `str` | - | Hex string, dashes removed |
| `size` | `int` | `2` | Chars per path segment |

---

### `WidPathResolver(size=2)`

OOP interface with a binary-search implementation of path location.

| Method | Description |
|--------|-------------|
| `resolve(wid, base_dir)` | Locate file via binary search. Raises `FileNotFoundError` if `base_dir` missing. |
| `path_at_level(wid, level)` | Build the **relative** path for `wid` at depth `level`. |
| `max_level(wid)` | Maximum depth level = `len(wid) // size - 1`. |
| `candidate_paths(wid, base_dir)` | All candidate paths from shallowest to deepest. |

---

## Comparison with Git object store

| Feature | Git object store | widpath |
|---------|------------------|---------|
| Hash algorithm | SHA1 / SHA256 | Any hex string (UUID, SHA, etc.) |
| Directory depth | Fixed 2 levels | Adaptive 1-16 levels |
| File format | Binary blobs | Caller-defined (JSON, etc.) |
| Multiple objects per file | No (1 object = 1 file) | Yes (bucket file holds many) |
| Split strategy | `git gc` packs loose objects | Caller splits bucket files on overflow |


## Comparison with Existing Solutions

### Several path manipulation libraries are commonly available on PyPI:
| Package / Type             | Key Features                                                       | Difference from `widpath`                                                                              |
| -------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| **widpath** (this package) | WID-based slicing, hierarchical path generation, and binary search | Specifically designed for WID management, enabling fast storage path discovery                         |
| `wildpath`                 | Wildcard-based access to data structures                           | Unrelated to hierarchical filesystem path organization                                                 |
| `path` / `path.py`         | More user-friendly path manipulation APIs                          | Focuses on path operations rather than WID-based hierarchical storage strategies                       |
| Standard Library `pathlib` | Object-oriented, cross-platform path handling                      | Provides general path operations only, without hierarchical partitioning or binary search capabilities |

### Conclusion

widpath introduces a dedicated hierarchical file organization and lookup mechanism tailored for WIDs. It complements existing general-purpose path libraries by providing efficient storage path management and fast lookup capabilities for large-scale WID-based datasets.

---

## 中文说明

**widpath** 将WID字符串（UUID4或任意等长十六进制ID）映射到分层文件路径，
避免单目录下文件过多，同时支持 O（1）级别的点查询，无需数据库。

### 核心原理

UUID4 去掉 `-` 后共32个十六进制字符，按每 2 字符分段得到 16 级路径：

```
4a3f9c2b...  -> 4a / 3f / 9c / 2b / ...
```

同一前缀的 WID 共存于同一个 JSON 文件。 文件过大时，调用方将其拆分为更深的子目录，
widpath 的 `locate` / `get_file_path` 自动找到正确的文件。

### 两种接口

- **`locate(base_dir, wid)`**: 顺序遍历，沿着已存在的子目录下探，遇到缺失则返回当前层文件路径。
- **`WidPathResolver.resolve(wid, base_dir)`**: 二分查找版本，在稀疏目录树上减少 stat 调用次数。

两者在相同文件系统状态下返回相同结果（见 `tests/test_locate.py::TestAlgorithmConsistency`）。

---

## Development

```bash
git clone https://github.com/junsxu/widpath
cd widpath
pip install -e ".[dev]"
pytest                     # run all tests (except perf)
pytest -m perf             # run performance benchmarks
ruff check widpath tests   # lint
mypy widpath               # type check
```

---

## License

MIT @ junsxu / silmoony.com
