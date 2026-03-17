# copier-py

A [copier](https://github.com/copier-org/copier) template for modern Python projects.

Equivalent to [cookiecutter-py](https://github.com/ryankanno/cookiecutter-py) but uses copier instead of cookiecutter.

## Usage

```bash
copier copy gh:ryankanno/copier-py /path/to/destination
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uvx copier copy gh:ryankanno/copier-py /path/to/destination
```

## Features

- [uv](https://github.com/astral-sh/uv) for dependency management
- [structlog](https://www.structlog.org/) for logging
- [mypy](https://mypy.readthedocs.io/) for static type checking
- [pytest](https://docs.pytest.org/) with hypothesis and mutmut
- [tox](https://tox.readthedocs.io/) for multi-version testing
- [Sphinx](https://www.sphinx-doc.org/) documentation (17 theme choices)
- [pdbp](https://github.com/mdmintz/pdbp) for debugging
- [konch](https://konch.readthedocs.io/) for interactive shell
- [pre-commit](https://pre-commit.com/) hooks (mypy, ruff, black, isort, commitlint, detect-secrets, typos, deptry)
- [Dockerfile](https://docs.docker.com/) with multi-stage builds
- [dunamai](https://github.com/mtkennerly/dunamai) for semantic versioning
- [Justfile](https://just.systems/) task runner
- [Dependabot](https://docs.github.com/en/code-security/dependabot) integration
- GitHub Actions (ci, publish, codeql, docs, hadolint, pr-labeler, pr-size-labeler, commitlint, trufflehog, release-drafter)
- Optional direnv support

## Template Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `project_name` | — | Human-readable project name |
| `package_name` | — | Python package name (snake_case) |
| `project_short_description` | — | One-line description |
| `author_name` | Ryan Kanno | Author's full name |
| `author_email` | ryankanno@localkinegrinds.com | Author's email |
| `project_url` | — | GitHub repository URL |
| `python_version` | 3.12 | Primary Python version |
| `sphinx_theme` | furo | Sphinx documentation theme |
| And more... | | See `copier.yml` for full list |

## Updating Projects

Projects created with this template can be updated when the template evolves:

```bash
copier update /path/to/project
```
