# copier-py Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a copier template (copier-py) that replicates cookiecutter-py's functionality using copier instead of cookiecutter.

**Architecture:** Subdirectory mode (`template/`) with `.jinja` suffix for templated files. Copier's native `_exclude`, `when`, and `validator` replace cookiecutter hooks. Root project mirrors cookiecutter-py's tooling (uv, tox, pre-commit, pytest).

**Tech Stack:** copier 9.7+, uv, tox, pytest, pre-commit, Jinja2

---

## Phase 1: Root Project Scaffold

### Task 1: Initialize git repo and create root config files

**Files:**
- Create: `pyproject.toml`
- Create: `tox.ini`
- Create: `Justfile`
- Create: `.gitignore`
- Create: `.pre-commit-config.yaml`
- Create: `.commitlint.config.mjs`
- Create: `LICENSE`
- Create: `README.md`
- Create: `CLAUDE.md`
- Create: `copier_py/__init__.py`
- Create: `tests/__init__.py`

### Task 2: Create copier.yml

**Files:**
- Create: `copier.yml`

Key design:
- `_subdirectory: template`
- `_templates_suffix: ".jinja"`
- `_exclude` with Jinja2 conditionals for optional files
- `when` conditionals for dependent questions
- `validator` for package_name and supported_python_versions
- `bool` type for all y/n toggles

## Phase 2: Template Config Files

### Task 3: Core template config files

**Files:**
- Create: `template/pyproject.toml.jinja`
- Create: `template/tox.ini.jinja`
- Create: `template/Justfile.jinja`
- Create: `template/README.md.jinja`
- Create: `template/LICENSE.jinja`
- Create: `template/HISTORY.rst.jinja`
- Create: `template/AUTHORS.rst.jinja`

### Task 4: Docker and static config files

**Files:**
- Create: `template/Dockerfile.jinja`
- Create: `template/docker-entrypoint.sh`
- Create: `template/.envrc`
- Create: `template/.gitignore`
- Create: `template/.pre-commit-config.yaml.jinja`
- Create: `template/.commitlint.config.js`
- Create: `template/.konchrc.jinja`
- Create: `template/.secrets.baseline`
- Create: `template/.dockerignore`
- Create: `template/_typos.toml`
- Create: `template/logging.yaml`

## Phase 3: Template Source Code

### Task 5: Python source and test files

**Files:**
- Create: `template/src/{{package_name}}/__init__.py.jinja`
- Create: `template/src/{{package_name}}/{{package_name}}.py.jinja`
- Create: `template/tests/__init__.py`
- Create: `template/tests/test_{{package_name}}.py.jinja`

## Phase 4: Template Docs

### Task 6: Sphinx documentation files

**Files:**
- Create: `template/docs/conf.py.jinja`
- Create: `template/docs/index.rst.jinja`
- Create: `template/docs/Makefile`
- Create: `template/docs/make.bat`
- Create: `template/docs/_static/.keep`
- Create: `template/docs/getting_started/getting_started.rst`
- Create: `template/docs/usage/usage.rst`
- Create: `template/docs/roadmap/roadmap.rst`
- Create: `template/docs/todo/todo.rst`

## Phase 5: Template GitHub Actions

### Task 7: Static workflow files (no copier vars)

**Files:**
- Create: `template/.github/dependabot.yml`
- Create: `template/.github/labeler.yml.jinja`
- Create: `template/.github/release-drafter.yml`
- Create: `template/.github/workflows/codeql-analysis.yml`
- Create: `template/.github/workflows/commitlint.yml`
- Create: `template/.github/workflows/hadolint.yml`
- Create: `template/.github/workflows/pr-labeler.yml`
- Create: `template/.github/workflows/pr-size-labeler.yml`
- Create: `template/.github/workflows/release-drafter.yml`
- Create: `template/.github/workflows/trufflehog.yml`

### Task 8: Templated workflow files (.jinja suffix with {% raw %} blocks)

**Files:**
- Create: `template/.github/workflows/ci.yml.jinja`
- Create: `template/.github/workflows/publish.yml.jinja`
- Create: `template/.github/workflows/docs.yml.jinja`
- Create: `template/.github/workflows/auto-approve-merge-dependabot.yml`

## Phase 6: Tests

### Task 9: Test fixtures and generation tests

**Files:**
- Create: `tests/conftest.py`
- Create: `tests/test_copier_generation.py`

## Phase 7: Verify

### Task 10: Test template generation and run tests
