#!/usr/bin/env python
#
# Copyright (c) 2026 Ryan Kanno <ryankanno@localkinegrinds.com>
#
# Distributed under terms of the MIT license.

"""Test fixtures for copier-py template generation tests."""

from itertools import product
from pathlib import Path

import pytest
from _pytest.fixtures import SubRequest


TEMPLATE_DIR = str(Path(__file__).parent.parent)


@pytest.fixture
def default_context(request: SubRequest) -> dict[str, object]:  # noqa: ARG001
    """Creates default prompt vals."""
    return {
        "author_name": "Ryan Kanno",
        "author_email": "ryankanno@localkinegrinds.com",
        "project_name": "Everybody go surf",
        "project_short_description": "This is a short description about Everybody go surf",
        "project_url": "https://github.com/ryankanno/copier-py",
        "project_license": "MIT",
        "github_repository_owner": "ryankanno",
        "package_name": "surf",
        "version": "0.0.1",
        "python_version": "3.11",
        "supported_python_versions": "3.11, 3.12, 3.13, pypy3.11",
        "uv_version": "0.0.1",
        "tox_version": "0.808.0",
        "sphinx_theme": "furo",
        "should_use_direnv": True,
        "should_create_author_files": True,
        "should_install_github_dependabot": True,
        "should_automerge_autoapprove_github_dependabot": True,
        "should_install_github_actions": True,
        "should_upload_coverage_to_codecov": True,
        "should_publish_to_testpypi": True,
        "should_publish_to_pypi": True,
        "should_publish_to_github_packages": False,
        "should_attach_to_github_release": False,
    }


@pytest.fixture(params=list(product([True, False], repeat=6)))
def context(request: SubRequest) -> dict[str, object]:
    """Parametrized context with all boolean combinations."""
    should_create_author_files = request.param[0]
    should_install_github_dependabot = request.param[1]
    should_automerge_autoapprove_github_dependabot = request.param[2]
    should_install_github_actions = request.param[3]
    should_publish_to_pypi = request.param[4]
    should_use_direnv = request.param[5]

    return {
        "author_name": "Ryan",
        "author_email": "ryankanno@localkinegrinds.com",
        "project_name": "Test Project",
        "project_short_description": "This is a test project",
        "project_url": "https://github.com/ryankanno/copier-py",
        "project_license": "MIT",
        "github_repository_owner": "ryankanno",
        "package_name": "test_project",
        "version": "0.0.1",
        "python_version": "3.11",
        "supported_python_versions": "3.11, 3.12, 3.13, pypy3.11",
        "uv_version": "0.7.3",
        "tox_version": "4.25.0",
        "sphinx_theme": "furo",
        "should_use_direnv": should_use_direnv,
        "should_create_author_files": should_create_author_files,
        "should_install_github_dependabot": should_install_github_dependabot,
        "should_automerge_autoapprove_github_dependabot": (
            should_automerge_autoapprove_github_dependabot
            and should_install_github_dependabot
            and should_install_github_actions
        ),
        "should_install_github_actions": should_install_github_actions,
        "should_upload_coverage_to_codecov": True,
        "should_publish_to_testpypi": should_publish_to_pypi,
        "should_publish_to_pypi": should_publish_to_pypi,
        "should_publish_to_github_packages": False,
        "should_attach_to_github_release": False,
    }


# vim: fenc=utf-8
# vim: filetype=python
