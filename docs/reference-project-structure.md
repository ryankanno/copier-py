# Generated Project Structure Reference

The file tree produced by copier-py with all options enabled. Files marked as conditional are only included based on configuration.

```
project-root/
├── .copier-answers.yml
├── .envrc                              # (conditional: should_use_direnv)
├── .github/
│   ├── dependabot.yml                  # (conditional: should_install_github_dependabot)
│   ├── labeler.yml                     # (conditional: should_install_github_actions)
│   ├── release-drafter.yml             # (conditional: should_install_github_actions)
│   └── workflows/                      # (conditional: should_install_github_actions)
│       ├── auto-approve-merge-dependabot.yml
│       ├── ci.yml
│       ├── codeql.yml
│       ├── commitlint.yml
│       ├── docs.yml
│       ├── hadolint.yml
│       ├── pr-labeler.yml
│       ├── pr-size-labeling.yml
│       ├── publish.yml
│       ├── release-drafter.yml
│       └── trufflehog.yml
├── .gitignore
├── .konchrc
├── .pre-commit-config.yaml
├── .secrets.baseline
├── AUTHORS.rst                         # (conditional: should_create_author_files)
├── Dockerfile
├── Justfile
├── LICENSE
├── README.md
├── commitlint.config.js
├── docs/
│   ├── Makefile
│   ├── _static/
│   ├── conf.py
│   ├── getting_started/
│   │   └── getting_started.rst
│   ├── index.rst
│   ├── make.bat
│   ├── roadmap/
│   │   └── roadmap.rst
│   ├── todo/
│   │   └── todo.rst
│   └── usage/
│       └── usage.rst
├── pyproject.toml
├── src/
│   └── {package_name}/
│       └── __init__.py
├── tests/
│   ├── conftest.py
│   └── test_{package_name}.py
└── tox.ini
```

## File descriptions

### Root files

| File | Description |
|------|-------------|
| `.copier-answers.yml` | Stores answers from copier generation. Used by `copier update` to remember previous choices. |
| `.envrc` | direnv configuration with `use uv` layout for automatic virtual environment activation. |
| `.gitignore` | Standard Python gitignore with additional entries for tox, coverage, and docs artifacts. |
| `.konchrc` | [konch](https://konch.readthedocs.io/) shell configuration with IPython support. |
| `.pre-commit-config.yaml` | Pre-commit hook configuration including ruff, mypy, bashate, commitlint, detect-secrets, typos, and deptry. |
| `.secrets.baseline` | Baseline file for detect-secrets to track known/allowed secrets. |
| `AUTHORS.rst` | Project authors list. |
| `commitlint.config.js` | Commitlint configuration enforcing [Conventional Commits](https://www.conventionalcommits.org/). |
| `Dockerfile` | Multi-stage Docker build with development, testing, and production stages. Final stage runs as a non-root user. |
| `Justfile` | Task runner commands wrapping uv, tox, and sphinx operations. Run `just` to see available commands. |
| `LICENSE` | Project license file. |
| `README.md` | Project documentation with badges, features, getting started, and usage sections. |
| `pyproject.toml` | Project metadata, dependencies, and tool configuration (ruff, mypy, pytest, coverage). |
| `tox.ini` | Tox configuration defining test, coverage, lint, and docs environments. |

### Source code

| Path | Description |
|------|-------------|
| `src/{package_name}/` | Package source directory using src layout. |
| `src/{package_name}/__init__.py` | Package init with `__version__` set to the configured version. |

### Tests

| Path | Description |
|------|-------------|
| `tests/conftest.py` | Shared pytest fixtures. |
| `tests/test_{package_name}.py` | Starter test verifying the package version. |

### Documentation

| Path | Description |
|------|-------------|
| `docs/conf.py` | Sphinx configuration with selected theme and MyST parser. |
| `docs/index.rst` | Documentation root page with toctree. |
| `docs/getting_started/` | Getting started documentation section. |
| `docs/usage/` | Usage documentation section. |
| `docs/roadmap/` | Roadmap documentation section. |
| `docs/todo/` | TODO tracking section. |

### GitHub configuration

| Path | Description |
|------|-------------|
| `.github/dependabot.yml` | Dependabot configuration for pip and GitHub Actions dependency updates. |
| `.github/labeler.yml` | PR labeler rules mapping file paths to labels. |
| `.github/release-drafter.yml` | Release drafter configuration for automated release notes. |

### GitHub Actions workflows

| Workflow | Trigger | Description |
|----------|---------|-------------|
| `ci.yml` | Push, PR | Runs tests across Python version matrix, linting, and type checking. |
| `publish.yml` | Push to main, release | Builds package and publishes to configured destinations. |
| `codeql.yml` | Push to main, weekly | CodeQL security analysis. |
| `hadolint.yml` | Push, PR | Dockerfile linting. |
| `commitlint.yml` | PR | Validates commit messages against Conventional Commits. |
| `trufflehog.yml` | Push, PR | Scans for leaked secrets. |
| `docs.yml` | Push to main, release | Builds and publishes Sphinx documentation to GitHub Pages. |
| `release-drafter.yml` | Push to main | Drafts release notes from merged PRs. |
| `pr-size-labeling.yml` | PR | Adds size labels (XS, S, M, L, XL) to PRs. |
| `pr-labeler.yml` | PR | Adds labels based on file paths changed. |
| `auto-approve-merge-dependabot.yml` | PR | Auto-approves and merges minor/patch Dependabot PRs. |
