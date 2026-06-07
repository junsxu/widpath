# Contributing to widpath

Thank you for considering a contribution!

## Local development setup

```bash
git clone https://github.com/junsxu/widpath
cd widpath
pip install -e ".[dev]"
```

## Running tests

```bash
pytest                      # all tests except perf benchmarks
pytest -m perf              # performance benchmarks only
pytest --cov-report=html    # generate HTML coverage report in htmlcov/
```

The CI gate requires **≥ 95% coverage**.

## Linting and type checking

```bash
ruff check widpath tests    # lint
ruff format widpath tests   # auto-format
mypy widpath                # strict type checking
```

All checks must pass before a PR can be merged.

## Branch naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feat/<short-desc>` | `feat/locate-function` |
| Bug fix | `fix/<short-desc>` | `fix/base-dir-missing` |
| Docs | `docs/<short-desc>` | `docs/readme-cn` |
| Refactor | `refactor/<short-desc>` | `refactor/pathlib-join` |

## Commit style

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add locate() functional interface
fix: raise FileNotFoundError when base_dir missing
docs: add Chinese README section
test: add edge cases for single-segment WID
```

## Pull request checklist

- [ ] Tests added or updated
- [ ] `pytest` passes locally (coverage ≥ 95 %)
- [ ] `ruff check` and `mypy` pass
- [ ] `CHANGELOG.md` updated under `[Unreleased]`
- [ ] PR description explains *why* the change is needed

## Release process (maintainers only)

1. Update `version` in `pyproject.toml` and `widpath/__init__.py`.
2. Move `[Unreleased]` entries in `CHANGELOG.md` to a new versioned section.
3. Commit: `chore: bump version to v0.x.y`.
4. Push to `main`, then create a **GitHub Release** with tag `v0.x.y`.
5. The `publish.yml` workflow triggers automatically and publishes to PyPI via
   OIDC Trusted Publishing (no API token required).
