# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Repository Overview

This is a [copier](https://github.com/copier-org/copier) template for modern Python projects. It generates a complete project scaffold with CI/CD, testing, documentation, and Docker support.

## Architecture

### Directory Structure
- `copier.yml` - Template configuration (questions, validators, excludes, tasks)
- `template/` - Template files (subdirectory mode)
- `template/src/{{package_name}}/` - Generated Python source code
- `template/.github/workflows/` - GitHub Actions workflow templates
- `template/docs/` - Sphinx documentation templates
- `copier_py/` - Root project Python package
- `tests/` - Template generation tests

### Template Design
- Uses copier's subdirectory mode (`_subdirectory: template`)
- Files with `.jinja` suffix are processed by Jinja2; others copied verbatim
- GitHub Actions `${{ }}` expressions wrapped in `{% raw %}` blocks
- Conditional files handled via `_exclude` in `copier.yml`
- Boolean questions use native `bool` type (not string y/n)

## Commands

### Testing
```bash
uv run pytest                    # Run tests
uv run pytest -x --no-header     # Run tests, stop on first failure
just tests                       # Run via tox
just coverage                    # Run with coverage
```

### Template Testing
```bash
# Generate a test project
copier copy . /tmp/test-output --defaults --trust
```

### Linting
```bash
just lint                        # Run linters
just lint --fix                  # Auto-fix issues
just pre-commit                  # Run all pre-commit hooks
```
