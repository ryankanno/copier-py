#!/usr/bin/env python
#
# Copyright (c) 2026 Ryan Kanno <ryankanno@localkinegrinds.com>
#
# Distributed under terms of the MIT license.

"""Tests project generation."""

import logging
import mmap
import os
import re
from pathlib import Path

import pytest
from binaryornot.check import is_binary
from copier import run_copy

LOGGER = logging.getLogger(__name__)

TEMPLATE_DIR = str(Path(__file__).parent.parent)

PATTERN = r"{{(\s?)((?!%|#|-)[a-z_].*?)}}"
RE_OBJ = re.compile(PATTERN)


EXPECTED_BASE_BAKED_FILES = [
    '.commitlint.config.js',
    '.dockerignore',
    '.gitignore',
    '.konchrc',
    '.pre-commit-config.yaml',
    '.secrets.baseline',
    'Dockerfile',
    'docker-entrypoint.sh',
    'HISTORY.rst',
    'LICENSE',
    'Justfile',
    'README.md',
    '/docs/Makefile',
    '/docs/conf.py',
    '/docs/index.rst',
    '/docs/make.bat',
    '/docs/_static/.keep',
    '/docs/getting_started/getting_started.rst',
    '/docs/roadmap/roadmap.rst',
    '/docs/todo/todo.rst',
    '/docs/usage/usage.rst',
    'logging.yaml',
    'pyproject.toml',
    'tox.ini',
    '_typos.toml',
]

EXPECTED_BAKED_DIRENV_FILES = ['.envrc']

EXPECTED_BAKED_AUTHORS_FILES = [
    'AUTHORS.rst',
]

EXPECTED_BAKED_GITHUB_DEPENDABOT_FILES = [
    '/.github/dependabot.yml',
]

EXPECTED_BAKED_GITHUB_AUTOAPPROVE_AUTOMERGE_DEPENDABOT_FILES = [
    '/.github/workflows/auto-approve-merge-dependabot.yml',
]

EXPECTED_BAKED_GITHUB_ACTIONS_FILES = [
    '/.github/labeler.yml',
    '/.github/release-drafter.yml',
    '/.github/workflows/ci.yml',
    '/.github/workflows/codeql-analysis.yml',
    '/.github/workflows/commitlint.yml',
    '/.github/workflows/docs.yml',
    '/.github/workflows/hadolint.yml',
    '/.github/workflows/pr-labeler.yml',
    '/.github/workflows/pr-size-labeler.yml',
    '/.github/workflows/release-drafter.yml',
    '/.github/workflows/trufflehog.yml',
]

EXPECTED_BAKED_GITHUB_ACTIONS_PYPI_PUBLISH_FILES = [
    '/.github/workflows/publish.yml',
]


def get_expected_baked_files(package_name: str) -> list[str]:
    """Get the expected list of baked files for a given package name."""
    return EXPECTED_BASE_BAKED_FILES + [
        f'/src/{package_name}/__init__.py',
        f'/src/{package_name}/{package_name}.py',
        '/tests/__init__.py',
        f'/tests/test_{package_name}.py',
    ]


def build_files_list(root_dir: str, is_absolute: bool = True) -> list[str]:
    """Build a list containing abs/relative paths to the generated files."""
    result = []
    for dirpath, subdirs, files in os.walk(root_dir):
        # Skip .git directory
        subdirs[:] = [d for d in subdirs if d != '.git']
        for file_path in files:
            if is_absolute:
                result.append(str(Path(dirpath) / file_path))
            else:
                result.append(
                    str(Path(dirpath[len(root_dir) :]) / file_path)
                )
    return result


def check_paths_substitution(paths: list[str]) -> None:
    """Verify no unrendered template variables remain in generated files."""
    for path in paths:
        if is_binary(path):
            continue
        with Path(path).open(encoding="utf-8") as f:
            for line in f:
                # Skip lines that are GitHub Actions expressions (${{ }})
                # or Jinja raw blocks or copier answer markers
                if '${{' in line or '{%' in line or '_copier_answers' in line:
                    continue
                match = RE_OBJ.search(line)
                if match:
                    # Allow legitimate double-brace usage in Justfiles
                    if path.endswith('Justfile'):
                        continue
                    assert (
                        match is None
                    ), f"template variable not replaced in {path}: {line.strip()}"


def check_paths_exist(
    expected_paths: list[str], baked_files: list[str]
) -> None:
    """Verify expected files exist in the generated project."""
    baked_files_no_pycache = filter(
        lambda x: '__pycache__' not in x, baked_files
    )

    baked_files_no_ruff = filter(
        lambda x: '.ruff_cache' not in x, list(baked_files_no_pycache)
    )

    expected_baked_files = list(baked_files_no_ruff)

    assert len(expected_paths) == len(expected_baked_files)

    for expected_path in expected_paths:
        assert expected_path in expected_baked_files


def generate_project(
    tmp_path: Path, data: dict[str, object]
) -> Path:
    """Generate a project from the template."""
    run_copy(
        TEMPLATE_DIR,
        str(tmp_path),
        data=data,
        defaults=True,
        unsafe=True,
        vcs_ref="HEAD",
    )
    return tmp_path


def test_with_default_configuration(
    tmp_path: Path, default_context: dict[str, object]
) -> None:
    """Test template generates correctly with default configuration."""
    dest = generate_project(tmp_path, default_context)

    assert dest.is_dir()

    abs_baked_files = build_files_list(str(dest))
    assert abs_baked_files
    check_paths_substitution(abs_baked_files)

    rel_baked_files = build_files_list(str(dest), is_absolute=False)
    assert rel_baked_files

    expected_files = (
        get_expected_baked_files(default_context['package_name'])
        + EXPECTED_BAKED_AUTHORS_FILES
        + EXPECTED_BAKED_GITHUB_ACTIONS_PYPI_PUBLISH_FILES
        + EXPECTED_BAKED_GITHUB_DEPENDABOT_FILES
        + EXPECTED_BAKED_DIRENV_FILES
        + EXPECTED_BAKED_GITHUB_AUTOAPPROVE_AUTOMERGE_DEPENDABOT_FILES
        + EXPECTED_BAKED_GITHUB_ACTIONS_FILES
    )

    check_paths_exist(expected_files, rel_baked_files)


def test_with_parameterized_configuration(  # noqa: C901, PLR0912, PLR0915
    tmp_path: Path, context: dict[str, object]
) -> None:
    """Test template generates correctly with parametrized configurations."""
    dest = generate_project(tmp_path, context)

    assert dest.is_dir()

    abs_baked_files = build_files_list(str(dest))
    assert abs_baked_files
    check_paths_substitution(abs_baked_files)

    rel_baked_files = build_files_list(str(dest), is_absolute=False)
    assert rel_baked_files

    LOGGER.info("author file: %s", context['should_create_author_files'])
    LOGGER.info("dependabot: %s", context['should_install_github_dependabot'])
    LOGGER.info(
        "automerge_autoapprove_dependabot: %s",
        context['should_automerge_autoapprove_github_dependabot'],
    )
    LOGGER.info("gh actions: %s", context['should_install_github_actions'])
    LOGGER.info("pypi: %s", context['should_publish_to_pypi'])
    LOGGER.info("direnv: %s", context['should_use_direnv'])

    expected_files = get_expected_baked_files(context['package_name'])

    if context['should_create_author_files']:
        expected_files += EXPECTED_BAKED_AUTHORS_FILES

    # publish.yml always exists when GitHub Actions is enabled
    if context['should_install_github_actions']:
        expected_files += EXPECTED_BAKED_GITHUB_ACTIONS_PYPI_PUBLISH_FILES

    if context['should_install_github_dependabot']:
        expected_files += EXPECTED_BAKED_GITHUB_DEPENDABOT_FILES

    if context['should_use_direnv']:
        expected_files += EXPECTED_BAKED_DIRENV_FILES

    if context['should_install_github_actions']:
        if context['should_automerge_autoapprove_github_dependabot']:
            check_paths_exist(
                expected_files
                + EXPECTED_BAKED_GITHUB_AUTOAPPROVE_AUTOMERGE_DEPENDABOT_FILES
                + EXPECTED_BAKED_GITHUB_ACTIONS_FILES,
                rel_baked_files,
            )
        else:
            check_paths_exist(
                expected_files + EXPECTED_BAKED_GITHUB_ACTIONS_FILES,
                rel_baked_files,
            )
    elif not context['should_install_github_actions']:
        check_paths_exist(
            list(
                set(expected_files)
                - set(EXPECTED_BAKED_GITHUB_ACTIONS_PYPI_PUBLISH_FILES)
            ),
            rel_baked_files,
        )
    else:
        pytest.fail('eeps. missed a case')


@pytest.mark.parametrize('codecov', [True, False])
def test_with_codecov(
    tmp_path: Path, default_context: dict[str, object], codecov: bool
) -> None:
    """Test codecov integration is conditionally included."""
    default_context['should_upload_coverage_to_codecov'] = codecov
    dest = generate_project(tmp_path, default_context)

    assert dest.is_dir()

    abs_baked_files = build_files_list(str(dest))

    for path in abs_baked_files:
        if 'ci.yml' in path:
            with (
                Path(path).open('rb', 0) as file,
                mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s,
            ):
                if s.find(b'codecov') == -1 and codecov:
                    pytest.fail('Should have codecov')
                elif s.find(b'codecov') != -1 and not codecov:
                    pytest.fail('Should not have codecov')


@pytest.mark.parametrize('publish_testpypi', [True, False])
def test_with_publish_to_testpypi(
    tmp_path: Path,
    default_context: dict[str, object],
    publish_testpypi: bool,
) -> None:
    """Test TestPyPI publishing is conditionally included."""
    default_context['should_publish_to_testpypi'] = publish_testpypi
    dest = generate_project(tmp_path, default_context)

    assert dest.is_dir()

    abs_baked_files = build_files_list(str(dest))

    for path in abs_baked_files:
        if 'publish.yml' in path:
            with (
                Path(path).open('rb', 0) as file,
                mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s,
            ):
                if (
                    s.find(b'publish_test_pypi:') == -1
                    and publish_testpypi
                ):
                    pytest.fail('Should have publish_test_pypi job')
                elif (
                    s.find(b'publish_test_pypi:') != -1
                    and not publish_testpypi
                ):
                    pytest.fail('Should not have publish_test_pypi job')


@pytest.mark.parametrize('publish_github_packages', [True, False])
def test_with_publish_to_github_packages(
    tmp_path: Path,
    default_context: dict[str, object],
    publish_github_packages: bool,
) -> None:
    """Test GitHub Packages publishing is conditionally included."""
    default_context['should_publish_to_github_packages'] = (
        publish_github_packages
    )
    dest = generate_project(tmp_path, default_context)

    assert dest.is_dir()

    abs_baked_files = build_files_list(str(dest))

    for path in abs_baked_files:
        if 'publish.yml' in path:
            with (
                Path(path).open('rb', 0) as file,
                mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s,
            ):
                if (
                    s.find(b'publish_github_packages:') == -1
                    and publish_github_packages
                ):
                    pytest.fail('Should have publish_github_packages job')
                elif (
                    s.find(b'publish_github_packages:') != -1
                    and not publish_github_packages
                ):
                    pytest.fail('Should not have publish_github_packages job')


@pytest.mark.parametrize('attach_release', [True, False])
def test_with_attach_to_github_release(
    tmp_path: Path,
    default_context: dict[str, object],
    attach_release: bool,
) -> None:
    """Test GitHub release attachment is conditionally included."""
    default_context['should_attach_to_github_release'] = attach_release
    dest = generate_project(tmp_path, default_context)

    assert dest.is_dir()

    abs_baked_files = build_files_list(str(dest))

    for path in abs_baked_files:
        if 'publish.yml' in path:
            with (
                Path(path).open('rb', 0) as file,
                mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s,
            ):
                if (
                    s.find(b'attach_to_release:') == -1
                    and attach_release
                ):
                    pytest.fail('Should have attach_to_release job')
                elif (
                    s.find(b'attach_to_release:') != -1
                    and not attach_release
                ):
                    pytest.fail('Should not have attach_to_release job')


@pytest.mark.parametrize(
    (
        'testpypi',
        'pypi',
        'github_packages',
        'attach_release',
        'expected_job_count',
    ),
    [
        # All disabled - file should STILL exist (with only build job)
        (False, False, False, False, 1),
        # Only TestPyPI enabled
        (True, False, False, False, 2),
        # Only PyPI enabled
        (False, True, False, False, 2),
        # Only GitHub Packages enabled
        (False, False, True, False, 2),
        # Only attach to release enabled
        (False, False, False, True, 2),
        # All enabled
        (True, True, True, True, 5),
    ],
)
def test_publish_yml_always_exists_with_github_actions(  # noqa: PLR0913, PLR0917
    tmp_path: Path,
    default_context: dict[str, object],
    testpypi: bool,
    pypi: bool,
    github_packages: bool,
    attach_release: bool,
    expected_job_count: int,
) -> None:
    """Test publish.yml always exists with correct job count."""
    default_context['should_publish_to_testpypi'] = testpypi
    default_context['should_publish_to_pypi'] = pypi
    default_context['should_publish_to_github_packages'] = github_packages
    default_context['should_attach_to_github_release'] = attach_release
    dest = generate_project(tmp_path, default_context)

    assert dest.is_dir()

    rel_baked_files = build_files_list(str(dest), is_absolute=False)

    publish_yml_path = '/.github/workflows/publish.yml'
    if publish_yml_path not in rel_baked_files:
        pytest.fail(
            'publish.yml should always exist when GitHub Actions is enabled'
        )

    # Count jobs in the workflow file
    abs_baked_files = build_files_list(str(dest))
    publish_yml = next(
        (path for path in abs_baked_files if 'publish.yml' in path), None
    )
    if not publish_yml:
        pytest.fail('Could not find publish.yml in baked files')

    with Path(publish_yml).open('r', encoding='utf-8') as file:
        content = file.read()

    # Count job definitions under "jobs:" section
    job_count = 0
    in_jobs_section = False
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped == 'jobs:':
            in_jobs_section = True
            continue
        if in_jobs_section and line and not line.startswith(' '):
            in_jobs_section = False
        # Count jobs: 2-space indent, ends with colon, not a comment
        is_job = (
            in_jobs_section
            and line.startswith('  ')
            and not line.startswith('    ')
            and stripped
            and not stripped.startswith('#')
            and stripped.endswith(':')
        )
        if is_job:
            job_count += 1

    if job_count != expected_job_count:
        pytest.fail(f'Expected {expected_job_count} jobs, found {job_count}')


@pytest.mark.parametrize('testpypi_enabled', [True, False])
def test_publish_pypi_job_dependencies(
    tmp_path: Path,
    default_context: dict[str, object],
    testpypi_enabled: bool,
) -> None:
    """Test PyPI job depends on TestPyPI when both enabled."""
    default_context['should_publish_to_testpypi'] = testpypi_enabled
    dest = generate_project(tmp_path, default_context)

    assert dest.is_dir()

    abs_baked_files = build_files_list(str(dest))

    publish_yml = next(
        (path for path in abs_baked_files if 'publish.yml' in path), None
    )
    if not publish_yml:
        return

    with (
        Path(publish_yml).open('rb', 0) as file,
        mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s,
    ):
        content = s.read().decode('utf-8')

    if 'publish_pypi:' not in content:
        return

    # Verify dependencies based on TestPyPI configuration
    has_testpypi_dep = 'needs: [build, publish_test_pypi]' in content
    has_build_only_dep = 'needs: [build]' in content

    if testpypi_enabled:
        if not has_testpypi_dep:
            msg = (
                'publish_pypi should depend on '
                '[build, publish_test_pypi] when TestPyPI is enabled'
            )
            pytest.fail(msg)
    else:
        if has_testpypi_dep:
            msg = (
                'publish_pypi should not depend on '
                'publish_test_pypi when TestPyPI is disabled'
            )
            pytest.fail(msg)
        if not has_build_only_dep:
            msg = (
                'publish_pypi should depend on '
                '[build] when TestPyPI is disabled'
            )
            pytest.fail(msg)


@pytest.mark.parametrize('uv_version', ['8.0.8', '4.2.0'])
def test_with_uv_version(
    tmp_path: Path,
    default_context: dict[str, object],
    uv_version: str,
) -> None:
    """Test uv version is correctly substituted."""
    default_context['uv_version'] = uv_version
    dest = generate_project(tmp_path, default_context)

    assert dest.is_dir()

    abs_baked_files = build_files_list(str(dest))

    for path in abs_baked_files:
        if 'Dockerfile' in path:
            with (
                Path(path).open('rb', 0) as file,
                mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s,
            ):
                if s.find(f"UV_VERSION={uv_version}".encode()) == -1:
                    pytest.fail('Should have appropriate uv version')


@pytest.mark.parametrize('tox_version', ['8.0.8', '4.2.0'])
def test_with_tox_version(
    tmp_path: Path,
    default_context: dict[str, object],
    tox_version: str,
) -> None:
    """Test tox version is correctly substituted."""
    default_context['tox_version'] = tox_version
    dest = generate_project(tmp_path, default_context)

    assert dest.is_dir()

    abs_baked_files = build_files_list(str(dest))

    for path in abs_baked_files:
        if 'ci.yml' in path:
            with (
                Path(path).open('rb', 0) as file,
                mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s,
            ):
                if s.find(f"TOX_VERSION: {tox_version}".encode()) == -1:
                    pytest.fail('Should have appropriate tox version')


@pytest.mark.parametrize('version', ['42.0', '4.2.0'])
def test_with_version(
    tmp_path: Path,
    default_context: dict[str, object],
    version: str,
) -> None:
    """Test version is correctly substituted in pyproject.toml."""
    default_context['version'] = version
    dest = generate_project(tmp_path, default_context)

    assert dest.is_dir()

    abs_baked_files = build_files_list(str(dest))

    for path in abs_baked_files:
        if 'pyproject.toml' in path:
            with (
                Path(path).open('rb', 0) as file,
                mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s,
            ):
                if s.find(f'version = "{version}"'.encode()) == -1:
                    pytest.fail(
                        'pyproject.toml should have appropriate version'
                    )


def test_justfile_lint_command_structure(
    tmp_path: Path,
    default_context: dict[str, object],
) -> None:
    """Verify the generated Justfile has the correct lint command structure."""
    dest = generate_project(tmp_path, default_context)

    assert dest.is_dir()

    abs_baked_files = build_files_list(str(dest))

    for path in abs_baked_files:
        if path.endswith('Justfile'):
            with Path(path).open('rb', 0) as file:
                content = file.read()

                if b'lint *LINT_ARGS:' not in content:
                    msg = 'Justfile should have lint recipe with '
                    msg += '*LINT_ARGS parameter'
                    pytest.fail(msg)

                if b'if [[ "{{LINT_ARGS}}" == "--fix" ]]' not in content:
                    pytest.fail(
                        'Justfile lint recipe should check for --fix flag'
                    )

                if b'just tox run -e lint-fix' not in content:
                    msg = 'Justfile should call tox lint-fix '
                    msg += 'environment when --fix is passed'
                    pytest.fail(msg)

                if b'just tox run -e lint {{LINT_ARGS}}' not in content:
                    pytest.fail(
                        'Justfile should call tox lint environment by default'
                    )


def test_pyproject_with_default_configuration(
    tmp_path: Path,
    default_context: dict[str, object],
) -> None:
    """Verify pyproject.toml has expected configuration sections."""
    dest = generate_project(tmp_path, default_context)

    assert dest.is_dir()

    abs_baked_files = build_files_list(str(dest))

    for path in abs_baked_files:
        if 'pyproject.toml' in path:
            with (
                Path(path).open('rb', 0) as file,
                mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s,
            ):
                if s.find(b'[tool.mypy]') == -1:
                    pytest.fail('Should have mypy configuration section')
                if s.find(b'[tool.ruff.lint]') == -1:
                    pytest.fail('Should have ruff lint configuration')


@pytest.mark.parametrize('python_version', ['3.10', '3.11', '3.12', '3.13'])
def test_with_python_version(
    tmp_path: Path,
    default_context: dict[str, object],
    python_version: str,
) -> None:
    """Verify generated project supports specified Python version."""
    default_context['python_version'] = python_version
    default_context['supported_python_versions'] = (
        "3.10, 3.11, 3.12, 3.13, pypy3.10, pypy3.11"
    )

    dest = generate_project(tmp_path, default_context)

    assert dest.is_dir()

    abs_baked_files = build_files_list(str(dest))

    for path in abs_baked_files:
        if 'pyproject.toml' in path:
            with (
                Path(path).open('rb', 0) as file,
                mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s,
            ):
                if (
                    s.find(
                        f"requires-python = \">={python_version}\"".encode()
                    )
                    == -1
                ):
                    pytest.fail(
                        f'pyproject.toml requires Python {python_version}'
                    )

    for path in abs_baked_files:
        if path.endswith('tox.ini'):
            with (
                Path(path).open('rb', 0) as file,
                mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ) as s,
            ):
                py_env = f"py{python_version.replace('.', '')}".encode()
                if s.find(py_env) == -1:
                    pytest.fail(
                        f'tox.ini should include {py_env.decode()} environment'
                    )


# vim: fenc=utf-8
# vim: filetype=python
