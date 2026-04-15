# Why These Tools?

This page explains the rationale behind the tools and patterns chosen for the copier-py template.

## uv for dependency management

[uv](https://docs.astral.sh/uv/) replaces pip, pip-tools, and virtualenv in a single tool written in Rust. It resolves and installs dependencies significantly faster than pip, supports lockfiles natively, and handles Python version management. The template uses uv as the primary package manager because it simplifies the developer experience — one tool handles what previously required three or four.

## ruff for linting and formatting

[ruff](https://docs.astral.sh/ruff/) consolidates flake8, isort, pyflakes, pycodestyle, and black into a single Rust-based tool. It runs orders of magnitude faster than the Python-based tools it replaces and enforces consistent style without requiring developers to configure multiple tools separately. The template uses ruff for linting, formatting, and import sorting.

## tox for test automation

[tox](https://tox.wiki/) provides reproducible test environments across multiple Python versions. While uv handles dependency management, tox manages the matrix of Python versions and test configurations (unit tests, coverage, linting, docs). This separation keeps `pyproject.toml` focused on project metadata and lets tox orchestrate the full test and quality pipeline.

## pytest with hypothesis and mutmut

[pytest](https://docs.pytest.org/) is the standard Python testing framework. The template adds [hypothesis](https://hypothesis.readthedocs.io/) for property-based testing — it generates test cases automatically to find edge cases that example-based tests miss. [mutmut](https://mutmut.readthedocs.io/) provides mutation testing, which verifies that your tests actually catch bugs by introducing small changes to source code and checking that tests fail. Together, these tools provide confidence beyond line coverage.

The template also includes [pytest-xdist](https://pytest-xdist.readthedocs.io/) for parallel test execution and [pytest-randomly](https://github.com/pytest-dev/pytest-randomly) to randomize test order, exposing hidden dependencies between tests.

## mypy for type checking

[mypy](https://mypy-lang.org/) catches type errors before runtime. Python's type system is optional, but mypy makes it useful — it finds bugs that tests might miss, like passing a string where an integer is expected. The template configures mypy in strict mode to maximize the value of type annotations.

## sphinx with MyST parser

[Sphinx](https://www.sphinx-doc.org/) is the established documentation tool for Python projects. The template adds [MyST parser](https://myst-parser.readthedocs.io/) to support writing documentation in Markdown alongside reStructuredText. This lowers the barrier for contributors who are more familiar with Markdown while retaining Sphinx's powerful cross-referencing, autodoc, and theme ecosystem.

The template offers 17 Sphinx themes. [Furo](https://pradyunsg.me/furo/) is the default because it provides a clean, modern design with dark mode support, good mobile responsiveness, and minimal configuration.

## pre-commit for automated checks

[pre-commit](https://pre-commit.com/) runs checks before each commit, catching issues early in the development cycle. The template configures hooks for:

- **ruff** — linting and formatting
- **mypy** — type checking
- **detect-secrets** — prevents accidental credential commits
- **commitlint** — enforces [Conventional Commits](https://www.conventionalcommits.org/) for consistent, parseable commit messages
- **bashate** — lints shell scripts
- **typos** — catches spelling mistakes in code and docs
- **deptry** — detects unused, missing, or transitive dependencies

Running these checks locally means developers get fast feedback without waiting for CI.

## src layout

The template uses a [src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) where package code lives under `src/`. This prevents accidental imports of the development version during testing — when you run `pytest`, Python imports from the installed package, not from the local directory. This catches packaging issues early that a flat layout would hide.

## Dockerfile with multi-stage build

The generated Dockerfile uses a multi-stage build with separate stages for development, testing, and production. This keeps the production image small (no dev dependencies) while providing full tooling in development. The final stage runs as a non-root user for security.

## GitHub Actions workflow design

The template generates separate workflows for distinct concerns rather than a single monolithic workflow:

- **CI** handles testing and quality checks on every push
- **Publish** handles package distribution on releases
- **Security workflows** (CodeQL, trufflehog) run on their own schedules

This separation means a failing security scan doesn't block CI, and CI failures don't prevent documentation builds. Each workflow uses GitHub environments for deployment protection where appropriate.

## Copier over Cookiecutter

This template uses [copier](https://copier.readthedocs.io/) instead of [cookiecutter](https://cookiecutter.readthedocs.io/) for project generation. Copier provides a key advantage: `copier update`. When the template evolves, projects generated from it can pull in improvements without manual diffing. Copier also supports conditional file inclusion, typed questions with validation, and Jinja2 templating with a cleaner configuration format.
