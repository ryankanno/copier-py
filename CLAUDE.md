# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modern Python copier template project that generates standardized Python project structures. The repository contains both the copier template source code and a template directory (`template/`) that serves as the blueprint for new projects. It is the copier equivalent of [cookiecutter-py](https://github.com/ryankanno/cookiecutter-py).

## Architecture

### Dual Structure
- **Root project**: The copier template itself with its own test suite and tooling
- **Template directory**: `template/` contains Jinja2-templated files that get rendered when users run copier (subdirectory mode via `_subdirectory: template` in `copier.yml`)
- **Configuration**: `copier.yml` defines template variables, defaults, choices, validators, conditional exclusions, and post-generation tasks

### Critical Architectural Patterns
- **Subdirectory mode**: Template files live in `template/`, cleanly separated from root project files
- **Template suffix**: Files with `.jinja` suffix are processed by Jinja2; others are copied verbatim
- **GitHub Actions expressions**: `${{ }}` in `.jinja` workflow files are wrapped in `{% raw %}...{% endraw %}` blocks to prevent Jinja2 processing
- **Template exclusions**: `pyproject.toml` excludes `template/` from mypy/ruff/black to prevent linting unrendered Jinja2 templates
- **Conditional files**: `copier.yml` `_exclude` rules conditionally remove files based on user selections (e.g., direnv, author files, Dependabot workflows). Note: `publish.yml` is never removed when GitHub Actions is enabled - it always builds and uploads artifacts even when all publish destinations are disabled.
- **Boolean questions**: Use native `bool` type (not string y/n like cookiecutter)
- **Validation**: `copier.yml` `validator` fields validate package_name and supported Python versions inline
- **Conditional questions**: `when` fields control question visibility (e.g., Dependabot automerge only shown when both Dependabot and GitHub Actions are enabled)
- **Test strategy**: Uses copier's Python API (`run_copy`) to test actual template generation, verifying that template variables are properly substituted and expected files exist

The template generates projects with:
- `uv` for dependency management
- `tox` for testing across Python versions (3.11, 3.12, 3.13, PyPy)
- `pytest` with coverage, xdist, randomly, mock, and hypothesis
- `ruff` for linting, formatting, and import sorting
- `mypy` for type checking
- `sphinx` for documentation with selectable themes
- Pre-commit hooks with comprehensive tooling (detect-secrets, commitlint, bashate, typos, deptry)
- GitHub Actions workflows:
  - CI with optional Codecov integration
  - CodeQL security analysis
  - Publish workflow with configurable destinations (TestPyPI, PyPI, GitHub Packages, GitHub Releases)
  - Auto-approve/merge Dependabot PRs
  - Additional workflows for hadolint, commitlint, trufflehog, docs, PR labeling
- Docker configuration for development and production

## Development Commands

All commands use `uv` as the package manager and `just` as the task runner.

### Primary Commands
- `just tests` - Run tests across all Python versions using tox (fast, no coverage)
- `just tests -- path/to/test.py` - Run specific test file
- `just tests -- --durations=10` - Show slowest 10 tests
- `just coverage` - Run tests with comprehensive coverage analysis
- `just lint` - Run ruff linting checks via tox
- `just lint --fix` - Auto-fix ruff linting issues
- `just pre-commit` - Run all pre-commit hooks
- `just clean` - Remove all build, test, and documentation artifacts
- `just install` - Install dependencies using uv

### Tox Environments
- `just tox run -e py311` - Run tests on Python 3.11
- `just tox run -e py312` - Run tests on Python 3.12
- `just tox run -e py313` - Run tests on Python 3.13
- `just tox run -e coverage-py312` - Run tests with coverage on Python 3.12
- `just tox run -e pre-commit` - Run pre-commit hooks
- `just tox run-parallel -m tests` - Run all test environments in parallel
- `just tox run-parallel -m coverage` - Run all coverage environments in parallel

### Template Testing
```bash
# Generate a test project
copier copy . /tmp/test-output --defaults --trust

# Run the parity test against cookiecutter-py
./scripts/parity-test.sh
```

### Testing
The project tests the copier template generation process:
- Tests use copier's Python API (`run_copy`) to test actual template generation
- Tests verify that all template variables are properly substituted in generated files
- Tests verify expected files exist based on user configuration choices
- Tests verify `_exclude` rules correctly remove conditional files
- Parameterized tests cover 64 boolean configuration combinations (2^6)
- Tests verify publish workflow job inclusion:
  - `test_with_publish_to_testpypi` - Verifies TestPyPI job is conditionally included
  - `test_with_publish_to_github_packages` - Verifies GitHub Packages job is conditionally included
  - `test_with_attach_to_github_release` - Verifies attach-to-release job is conditionally included
  - `test_publish_yml_always_exists_with_github_actions` - Verifies workflow always exists and validates job counts
  - `test_publish_pypi_job_dependencies` - Verifies publish_pypi dependencies are correct
- Tests verify Dockerfile structure:
  - `test_dockerfile_structure` - Verifies multi-stage build stages exist, COPY --from references are valid, no unrendered template variables, and final stage runs as non-root user

### Key Configuration Files
- `copier.yml` - Template variables, defaults, choices, validators, excludes, and tasks
- `pyproject.toml` - Main project configuration, dependencies, tool settings (mypy, ruff, pytest, coverage)
- `tox.ini` - Multi-Python testing configuration with test/coverage/lint environments
- `Justfile` - Task runner commands wrapping common operations
- `scripts/parity-test.sh` - Parity test comparing copier-py output against cookiecutter-py output

## Important Considerations

When working with this codebase, be aware that changes may affect both:
1. The copier template infrastructure itself (tests, root configuration)
2. The generated project template in `template/` (files that end users will receive)

When modifying template files in `template/`:
- Files with `.jinja` suffix are processed by Jinja2; use `{{ variable_name }}` syntax (no `cookiecutter.` prefix)
- Use `{% raw %}...{% endraw %}` around GitHub Actions `${{ }}` expressions in `.jinja` files
- Static files without `.jinja` suffix are copied verbatim — `${{ }}` expressions are preserved as-is
- Test with `just tests` to verify substitution works correctly
- Run `./scripts/parity-test.sh` to verify output matches cookiecutter-py
