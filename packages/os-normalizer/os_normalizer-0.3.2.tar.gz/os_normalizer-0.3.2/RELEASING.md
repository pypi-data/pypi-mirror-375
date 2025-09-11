# Releasing to PyPI

This project uses a modern PEP 621 `pyproject.toml` with the Hatchling build backend. Below are the steps to build and publish to TestPyPI and PyPI using uv (recommended) or Twine.

## Prereqs

- Python 3.11+
- `uv` installed (https://github.com/astral-sh/uv)
- PyPI accounts and API tokens for TestPyPI and/or PyPI

## Project metadata checklist

- Verify `pyproject.toml` fields:
  - `name`, `version`, `description`, `readme`, `requires-python`
  - `classifiers`, `keywords`, `license`
  - `project.urls` (Homepage/Repository/Issues/Changelog)
- Ensure `LICENSE` exists and matches the license in `pyproject.toml`.
- Ensure `README.md` renders nicely on PyPI (use Markdown; referenced images should be absolute URLs).
- Update `CHANGELOG.md` with the release version and date.
- Optionally add `__version__` if you want a runtime version attribute.

## Run tests and lint

- `uv run --group dev pytest -q`
- Optionally: `uv run --group dev ruff check .`

## Build distributions

Using uv’s build:

- `uv build`  # builds both sdist and wheel into `dist/`

Alternatively using `build`:

- `uvx build`  # ephemeral install of the build frontend

## Verify distributions locally

- `uvx twine check dist/*`

## Publish to TestPyPI first (recommended)

1) Create a TestPyPI API token (https://test.pypi.org/manage/account/token/).
2) Upload:
   - `uvx twine upload --repository testpypi dist/*`
3) Install and smoke test from TestPyPI in a clean env:
   - `uv venv -p 3.11 .release-test`
   - `uv run --python .release-test/bin/python -m pip install -U pip`
   - `uv run --python .release-test/bin/python -m pip install -i https://test.pypi.org/simple/ os-normalizer`
   - `uv run --python .release-test/bin/python -c "import os_normalizer as m; print(m.__all__)"`

## Publish to PyPI

1) Create a PyPI API token (https://pypi.org/manage/account/token/).
2) Upload:
   - `uvx twine upload dist/*`

## Versioning and tagging

- Update `version` in `pyproject.toml` following SemVer (e.g., 0.3.2) by running
  - `uv version --bump <major|minor|patch> --dry-run`  <- confirm that's what you want
  - `uv version --bump <major|minor|patch>`

- Tag the release in git once published:
  - `git tag -a v0.3.2 -m "Release 0.3.2"`
  - `git push origin v0.3.2`

## Post-release

- Bump to the next dev version if desired (e.g. `0.3.3.dev0`).
- Open an issue for any follow-ups or hotfixes discovered after release.
