#!/usr/bin/env just --justfile

set quiet

runner_cmd := 'uv'

[private]
default:
    just --list

# Remove build artifacts (build, dist, .egg)
[private]
clean-build:
    rm -fr build/
    rm -fr dist/
    rm -fr .eggs/
    find . -name '*.egg-info' -exec rm -fr {} +
    find . -name '*.egg' -exec rm -fr {} +

# Remove Python artifacts (.pyc, .pyo, __pycache__)
[private]
clean-pyc:
    find . -name '*.pyc' -exec rm -f {} +
    find . -name '*.pyo' -exec rm -f {} +
    find . -name '*~' -exec rm -f {} +
    find . -name '__pycache__' -exec rm -fr {} +

# Remove test artifacts (.tox, .coverage, coveragexml)
[private]
clean-test:
    rm -fr .tox/
    rm -f .coverage
    rm -f coverage.xml
    rm -fr htmlcov/

# Remove build, Python, test artifacts
clean: clean-build clean-pyc clean-test

# Check code coverage with current Python
coverage:
    just tox run-parallel -m coverage

# Lint (tox:lint) - use --fix to auto-fix issues
lint *LINT_ARGS:
    @if [[ "{{LINT_ARGS}}" == "--fix" ]]; then \
        just tox run -e lint-fix; \
    else \
        just tox run -e lint {{LINT_ARGS}}; \
    fi

# Runs tests (tox:tests)
tests *TESTS_ARGS:
    just tox run-parallel -m tests {{TESTS_ARGS}}

# Runs pre-commit (tox:pre-commit)
pre-commit:
    just tox run -e pre-commit

# Runs tox
tox *TOX_ARGS:
    {{runner_cmd}} run tox {{TOX_ARGS}}
