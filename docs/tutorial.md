# Tutorial: Create Your First Python Project

This tutorial walks you through generating a Python project with copier-py, exploring its structure, running tests, and building documentation. By the end, you have a fully functional Python package ready for development.

## Prerequisites

You need [uv](https://docs.astral.sh/uv/) installed. If you don't have it yet:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Install [copier](https://copier.readthedocs.io/en/latest/) using uv:

```sh
uv tool install copier
```

## Generate the project

Run copier to create a new project. We use `--trust` to allow the post-generation `git init` task to run automatically:

```sh
copier copy gh:ryankanno/copier-py my-awesome-project --trust
```

Copier prompts you for configuration values. For this tutorial, accept the defaults by pressing Enter for each prompt. You can always change these later.

You see output like this as copier asks each question:

```
🎤 Author's full name
   Your Name
🎤 Author's email address
   you@example.com
🎤 Human-readable project name
   my-awesome-project
🎤 Python package name (snake_case)
   my_awesome_project
...
```

Once complete, copier creates the project directory and initializes a git repository.

## Explore the project structure

Change into your new project:

```sh
cd my-awesome-project
```

List the contents:

```sh
ls -la
```

You see a structure like this:

```
.
├── .envrc                  # direnv configuration
├── .github/                # GitHub Actions workflows
├── .pre-commit-config.yaml # Pre-commit hooks
├── AUTHORS.rst             # Project authors
├── Dockerfile              # Multi-stage Docker build
├── Justfile                # Task runner commands
├── LICENSE                 # MIT license
├── README.md               # Project documentation
├── docs/                   # Sphinx documentation
├── pyproject.toml          # Project metadata and dependencies
├── src/
│   └── my_awesome_project/ # Your package source code
│       └── __init__.py
├── tests/                  # Test directory
│   ├── conftest.py
│   └── test_my_awesome_project.py
└── tox.ini                 # Test automation configuration
```

The project is organized as a [src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) — your package code lives under `src/`.

## Install dependencies

Use `just` to install the project dependencies:

```sh
just install
```

This runs `uv sync` under the hood, creating a virtual environment and installing all dependencies.

## Run the tests

Run the test suite:

```sh
just tests
```

You see tox invoke pytest across your configured Python versions:

```
py312: commands[0]> uv run pytest tests/ -n auto --randomly-seed=default
========================= test session starts ==========================
collected 1 item

tests/test_my_awesome_project.py::test_version PASSED

========================= 1 passed in 0.12s ===========================
```

The template includes a starter test that verifies your package version is set correctly.

## Run the linter

Check your code with ruff:

```sh
just lint
```

Ruff checks for style issues, import ordering, and common errors. To auto-fix issues:

```sh
just lint --fix
```

## Build the documentation

Build the Sphinx documentation:

```sh
just docs
```

Sphinx generates HTML documentation in `.tox/docs_out/`. Open it in your browser:

```sh
open .tox/docs_out/index.html  # macOS
# xdg-open .tox/docs_out/index.html  # Linux
```

## Run pre-commit hooks

Install and run the pre-commit hooks:

```sh
uv run pre-commit install
uv run pre-commit run --all-files
```

The hooks check for secrets, validate commit messages, run the linter, and more.

## Make your first commit

Stage and commit the generated project:

```sh
git add -A
git commit -m "feat: initial project from copier-py template"
```

## Next steps

Your project is ready for development. From here you can:

- Add your package code under `src/my_awesome_project/`
- Write tests in `tests/`
- Push to GitHub to activate the CI workflows
- See the [How-to: Set Up Publishing to PyPI](howto-publishing.md) guide to configure package publishing
- See the [How-to: Configure CI with GitHub Actions](howto-ci.md) guide for CI customization
