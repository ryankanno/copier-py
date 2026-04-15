# Configuration Variables Reference

All variables defined in `copier.yml` that are prompted during project generation.

## Project information

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `author_name` | string | `"Ryan Kanno"` | Author's full name |
| `author_email` | string | `"ryankanno@localkinegrinds.com"` | Author's email address |
| `project_name` | string | — | Human-readable project name |
| `project_short_description` | string | `"This is a short description about {project_name}"` | One-line project description |
| `project_url` | string | `"https://github.com/ryankanno/copier-py"` | Project repository URL |
| `project_license` | string | `"MIT"` | Project license |
| `github_repository_owner` | string | `"ryankanno"` | GitHub repository owner |
| `package_name` | string | — | Python package name. Must be a valid Python identifier in snake_case (matches `^[a-z][a-z0-9_]*$`). |
| `version` | string | `"0.0.0"` | Initial project version |

## Python and tooling

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `python_version` | string | `"3.12"` | Primary Python version |
| `supported_python_versions` | string | `"3.11, 3.12, 3.13, pypy3.11"` | Comma-separated list of supported Python versions. Allowed values: `3.11`, `3.12`, `3.13`, `pypy3.11`. |
| `uv_version` | string | `"0.7.3"` | Version of uv to use |
| `tox_version` | string | `"4.25.0"` | Version of tox to use |

## Sphinx theme

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `sphinx_theme` | choice | `furo` | Documentation theme |

Available themes:

**Third-party themes:** `furo`, `sphinx-rtd-theme`, `sphinx-book-theme`, `pydata-sphinx-theme`, `sphinx-press-theme`, `piccolo-theme`, `sphinxawesome-theme`, `sphinx-wagtail-theme`

**Built-in themes:** `alabaster`, `agogo`, `bizstyle`, `classic`, `haiku`, `nature`, `pyramid`, `scrolls`, `sphinxdoc`, `traditional`

## Optional features

| Variable | Type | Default | Condition | Description |
|----------|------|---------|-----------|-------------|
| `should_use_direnv` | bool | `true` | — | Include `.envrc` for direnv environment management |
| `should_create_author_files` | bool | `true` | — | Include `AUTHORS.rst` |
| `should_install_github_dependabot` | bool | `true` | — | Include Dependabot configuration |
| `should_automerge_autoapprove_github_dependabot` | bool | `true` | Dependabot and GitHub Actions enabled | Auto-approve and auto-merge Dependabot PRs |
| `should_install_github_actions` | bool | `true` | — | Include GitHub Actions workflows |
| `should_upload_coverage_to_codecov` | bool | `false` | GitHub Actions enabled | Upload test coverage to Codecov |

## Publishing options

All publishing options require GitHub Actions to be enabled.

| Variable | Type | Default | Trigger | Description |
|----------|------|---------|---------|-------------|
| `should_publish_to_testpypi` | bool | `false` | Push to main | Publish to TestPyPI |
| `should_publish_to_pypi` | bool | `false` | GitHub release | Publish to PyPI |
| `should_publish_to_github_packages` | bool | `false` | GitHub release | Publish to GitHub Packages |
| `should_attach_to_github_release` | bool | `false` | GitHub release | Attach build artifacts to GitHub release |

Even with all publishing options disabled, the `publish.yml` workflow still runs the `build` job and uploads artifacts to GitHub Actions for manual inspection.

## File exclusions

Files are conditionally excluded based on configuration:

| File | Excluded when |
|------|---------------|
| `.envrc` | `should_use_direnv` is false |
| `AUTHORS.rst` | `should_create_author_files` is false |
| `.github/dependabot.yml` | `should_install_github_dependabot` is false |
| `.github/workflows/auto-approve-merge-dependabot.yml` | Dependabot, GitHub Actions, or auto-merge is false |
| `.github/labeler.yml` | `should_install_github_actions` is false |
| `.github/release-drafter.yml` | `should_install_github_actions` is false |
| `.github/workflows/` | `should_install_github_actions` is false |
