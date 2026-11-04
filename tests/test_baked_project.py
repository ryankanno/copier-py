#!/usr/bin/env python
#
# Copyright (c) 2026 Ryan Kanno <ryankanno@localkinegrinds.com>
#
# Distributed under terms of the MIT license.

"""Runs a generated project end to end."""

import json
import os
import shutil
import subprocess
from itertools import takewhile
from pathlib import Path

import pytest
from copier import run_copy

from tests.test_copier_generation import THIRD_PARTY_SPHINX_THEMES


TEMPLATE_DIR = str(Path(__file__).parent.parent)

# tox exports these for *this* project. Left set, uv would sync the baked
# project into this repo's environment rather than its own.
INHERITED_ENV_VARS = ('VIRTUAL_ENV', 'UV_PROJECT_ENVIRONMENT')

TIMEOUT_SECONDS = 900

HADOLINT_IMAGE = 'hadolint/hadolint:latest'
IMAGE_TAG = 'copier-py-baked:test'

# copier requires these regardless of --defaults; everything else falls
# back to the real copier.yml defaults, which is what a user receives.
REQUIRED_ANSWERS = {
    'project_name': 'Foobar',
    'package_name': 'foobar',
    'project_short_description': 'A foobar project',
    'project_url': 'https://github.com/ryankanno/foobar',
}

GIT_WITH_IDENTITY = [
    'git',
    '-c',
    'user.name=test',
    '-c',
    'user.email=test@example.com',
]

# Width of `        ` before the keys of a workflow step.
STEP_INDENT = 8

# Width of `          ` before the script lines of a workflow step.
STEP_SCRIPT_INDENT = 10


def run(
    command: list[str], cwd: Path, check: bool = True
) -> subprocess.CompletedProcess[str]:
    executable = shutil.which(command[0])
    assert executable is not None, f'{command[0]} is not installed'

    env = {
        key: value
        for key, value in os.environ.items()
        if key not in INHERITED_ENV_VARS
    }

    result = subprocess.run(
        [executable, *command[1:]],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
        check=False,
    )

    if check and result.returncode != 0:
        pytest.fail(
            f'{" ".join(command)} failed in {cwd}\n'
            f'stdout:\n{result.stdout}\n'
            f'stderr:\n{result.stderr}'
        )

    return result


def bake_with_real_defaults(tmp_path: Path, **answers: str) -> Path:
    """Generate a project using copier.yml's own defaults.

    Deliberately not the default_context fixture, which carries placeholder
    versions such as uv_version "0.0.1" to prove substitution happened.
    Those do not resolve as real releases or image tags.
    """
    run_copy(
        TEMPLATE_DIR,
        str(tmp_path),
        data={**REQUIRED_ANSWERS, **answers},
        defaults=True,
        unsafe=True,
        vcs_ref='HEAD',
    )
    return tmp_path


def workflow_step_script(workflow: Path, name: str) -> str:
    """The `run: |` script of the named step in a workflow file."""
    lines = workflow.read_text(encoding='utf-8').splitlines()
    step = f'      - name: {name}'
    assert step in lines, f'{workflow.name} has no step named {name!r}'

    after_step = lines[lines.index(step) + 1 :]
    step_lines = list(
        takewhile(
            lambda line: (
                not line.strip() or line.startswith(' ' * STEP_INDENT)
            ),
            after_step,
        )
    )
    assert '        run: |' in step_lines, f'step {name!r} has no run script'
    body = step_lines[step_lines.index('        run: |') + 1 :]

    script = []
    for line in body:
        if line.strip() and not line.startswith(' ' * STEP_SCRIPT_INDENT):
            break
        script.append(line[STEP_SCRIPT_INDENT:])
    return '\n'.join(script)


def commit_and_push(checkout: Path, branch: str) -> None:
    run(['git', 'add', '-A'], cwd=checkout)
    run([*GIT_WITH_IDENTITY, 'commit', '-m', 'seed'], cwd=checkout)
    run(['git', 'push', 'origin', branch], cwd=checkout)


def clone_for_pages_deploy(tmp_path: Path, has_pages_branch: bool) -> Path:
    """A clone of the default branch, as the deploy job's checkout makes."""
    remote = tmp_path / 'remote.git'
    seed = tmp_path / 'seed'
    run(
        ['git', 'init', '--bare', '--initial-branch=main', str(remote)],
        cwd=tmp_path,
    )
    run(['git', 'clone', str(remote), str(seed)], cwd=tmp_path)

    (seed / 'README.md').write_text('source\n', encoding='utf-8')
    commit_and_push(seed, 'main')

    # Shares a suffix with gh-pages, so it must not count as that branch.
    run(['git', 'push', 'origin', 'main:docs/gh-pages'], cwd=seed)

    if has_pages_branch:
        run(['git', 'checkout', '--orphan', 'gh-pages'], cwd=seed)
        run(['git', 'rm', '-rf', '--quiet', '.'], cwd=seed)
        (seed / 'versions.json').write_text('[]\n', encoding='utf-8')
        commit_and_push(seed, 'gh-pages')

    checkout = tmp_path / 'checkout'
    run(
        ['git', 'clone', '--branch', 'main', str(remote), str(checkout)],
        cwd=tmp_path,
    )
    return checkout


@pytest.mark.bake
@pytest.mark.parametrize('has_pages_branch', [False, True])
def test_docs_deploy_starts_from_the_published_branch(
    tmp_path: Path, has_pages_branch: bool
) -> None:
    project = bake_with_real_defaults(tmp_path / 'project')
    checkout = clone_for_pages_deploy(tmp_path, has_pages_branch)

    script = workflow_step_script(
        project / '.github' / 'workflows' / 'docs.yml',
        'Select gh-pages branch',
    )
    run(['bash', '-c', script], cwd=checkout)

    branch = run(['git', 'branch', '--show-current'], cwd=checkout)
    assert branch.stdout.strip() == 'gh-pages'

    # Source files must never reach the published site.
    assert not (checkout / 'README.md').exists()
    assert (checkout / 'versions.json').exists() == has_pages_branch

    (checkout / 'latest').mkdir()
    (checkout / 'latest' / 'index.html').write_text('docs\n', encoding='utf-8')
    commit_and_push(checkout, 'gh-pages')

    published = run(
        ['git', 'ls-remote', '--exit-code', '--heads', 'origin', 'gh-pages'],
        cwd=checkout,
    )
    assert published.stdout


@pytest.mark.bake
def test_docs_deploy_lists_every_published_version(tmp_path: Path) -> None:
    project = bake_with_real_defaults(tmp_path / 'project')
    pages = tmp_path / 'pages'
    for name in (
        'latest',
        'v1.2.3',
        'v1.10.0',
        '1.2.3-1',
        '1.2.3-rc1',
        '1.2.3-²',
        '_static',
    ):
        (pages / name).mkdir(parents=True)

    script = workflow_step_script(
        project / '.github' / 'workflows' / 'docs.yml',
        'Regenerate versions.json',
    )
    run(
        ['env', 'REPO_OWNER=acme', 'REPO_NAME=foo', 'bash', '-c', script],
        cwd=pages,
    )

    versions = json.loads((pages / 'versions.json').read_text('utf-8'))
    assert [version['name'] for version in versions] == [
        'latest',
        'v1.10.0',
        'v1.2.3',
        '1.2.3-1',
        '1.2.3-rc1',
        '1.2.3-²',
    ]


def determine_destination(
    tmp_path: Path, event: str, version: str
) -> subprocess.CompletedProcess[str]:
    project = bake_with_real_defaults(tmp_path / 'project')
    script = workflow_step_script(
        project / '.github' / 'workflows' / 'docs.yml',
        'Determine destination directory',
    )
    return run(
        [
            'env',
            f'EVENT_NAME={event}',
            f'RELEASE_TAG={version if event == "release" else ""}',
            f'INPUT_VERSION={version if event == "workflow_dispatch" else ""}',
            f'GITHUB_OUTPUT={tmp_path / "github_output"}',
            'bash',
            '-c',
            script,
        ],
        cwd=tmp_path,
        check=False,
    )


@pytest.mark.bake
@pytest.mark.parametrize(
    ('event', 'version', 'directory'),
    [
        ('push', '', 'latest'),
        ('workflow_dispatch', '', 'latest'),
        ('workflow_dispatch', 'v1.2.3', 'v1.2.3'),
        ('release', '1.2.3-rc1', '1.2.3-rc1'),
    ],
)
def test_docs_deploy_picks_the_version_directory(
    tmp_path: Path, event: str, version: str, directory: str
) -> None:
    result = determine_destination(tmp_path, event, version)

    assert result.returncode == 0, result.stderr
    output = tmp_path / 'github_output'
    assert output.read_text(encoding='utf-8') == f'dir={directory}\n'


@pytest.mark.bake
@pytest.mark.parametrize(
    ('event', 'version'),
    [
        ('workflow_dispatch', 'x"; touch injected; echo "'),
        ('workflow_dispatch', 'stable'),
        ('workflow_dispatch', '.git'),
        ('workflow_dispatch', '../artifact'),
        ('workflow_dispatch', '1.2.3-/../../.git'),
        ('workflow_dispatch', '1.2.3\nextra=1'),
        ('release', '../artifact'),
    ],
)
def test_docs_deploy_refuses_a_version_it_cannot_list(
    tmp_path: Path, event: str, version: str
) -> None:
    result = determine_destination(tmp_path, event, version)

    assert result.returncode != 0
    assert '::error::The version must be' in result.stdout
    assert not (tmp_path / 'injected').exists()
    assert not (tmp_path / 'github_output').exists()


# Stands in for the GitHub CLI, which the step calls over the network. It
# logs each call and answers `gh pr view` with the labels in FAKE_LABELS.
# FAKE_BODY_FAILS makes the body lookup fail, as an API error would.
FAKE_GH = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$GH_LOG"
case "$*" in
  *"--json labels"*) printf '%s\\n' $FAKE_LABELS ;;
  *"--json body"*)
    [ -z "$FAKE_BODY_FAILS" ] || exit 1
    echo 'Bumps foo from 1.0 to 1.1.' ;;
esac
"""

PR_URL = 'https://github.com/ryankanno/foobar/pull/7'


def auto_merge(
    tmp_path: Path, labels: str, body_fails: bool = False
) -> list[str]:
    project = bake_with_real_defaults(tmp_path / 'project')
    script = workflow_step_script(
        project
        / '.github'
        / 'workflows'
        / 'auto-approve-merge-dependabot.yml',
        'Auto merge',
    )
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    fake_gh = bin_dir / 'gh'
    fake_gh.write_text(FAKE_GH, encoding='utf-8')
    fake_gh.chmod(0o755)
    gh_log = tmp_path / 'gh.log'
    gh_log.touch()

    run(
        [
            'env',
            f'PATH={bin_dir}{os.pathsep}{os.environ["PATH"]}',
            f'GH_LOG={gh_log}',
            f'FAKE_LABELS={labels}',
            f'PR_URL={PR_URL}',
            f'FAKE_BODY_FAILS={"1" if body_fails else ""}',
            # The command GitHub runs for a step with `shell: bash`.
            'bash',
            '--noprofile',
            '--norc',
            '-eo',
            'pipefail',
            '-c',
            script,
        ],
        cwd=tmp_path,
        check=not body_fails,
    )
    return gh_log.read_text(encoding='utf-8').splitlines()


@pytest.mark.bake
def test_dependabot_auto_merge_squashes_a_pr_labeled_automerge(
    tmp_path: Path,
) -> None:
    calls = auto_merge(tmp_path, 'automerge dependencies')

    assert (
        f'pr merge {PR_URL} --squash --body Bumps foo from 1.0 to 1.1.'
        in calls
    )


@pytest.mark.bake
@pytest.mark.parametrize(
    'labels', ['dependencies', 'github-actions', 'automerge major']
)
def test_dependabot_auto_merge_leaves_other_prs_open(
    tmp_path: Path, labels: str
) -> None:
    calls = auto_merge(tmp_path, labels)

    assert not [call for call in calls if call.startswith('pr merge')]


@pytest.mark.bake
def test_dependabot_auto_merge_stops_when_the_body_lookup_fails(
    tmp_path: Path,
) -> None:
    calls = auto_merge(tmp_path, 'automerge dependencies', body_fails=True)

    assert not [call for call in calls if call.startswith('pr merge')]


@pytest.mark.bake
@pytest.mark.parametrize('sphinx_theme', THIRD_PARTY_SPHINX_THEMES)
def test_baked_project_resolves_with_theme(
    tmp_path: Path, sphinx_theme: str
) -> None:
    project = bake_with_real_defaults(tmp_path, sphinx_theme=sphinx_theme)

    # The theme lives in the docs group, which uv lock always resolves.
    run(['uv', 'lock'], cwd=project)


@pytest.mark.bake
def test_baked_project_runs(tmp_path: Path) -> None:
    project = bake_with_real_defaults(tmp_path)

    # The bootstrap the generated README documents. Creates uv.lock.
    run(['uv', 'sync'], cwd=project)

    # Every tox env in the generated project runs this, so a missing or
    # inconsistent lock breaks that project's own CI before it starts.
    run(['uv', 'sync', '--locked'], cwd=project)

    run(['uv', 'run', 'pytest'], cwd=project)
    run(['uv', 'run', 'ruff', 'check', '.'], cwd=project)


@pytest.mark.docker
def test_baked_project_docker_image(tmp_path: Path) -> None:
    project = bake_with_real_defaults(tmp_path)

    # The Dockerfile does `COPY uv.lock`, which does not exist until the
    # documented bootstrap has run.
    run(['uv', 'lock'], cwd=project)

    # hadolint cannot parse the template itself, only a rendered Dockerfile,
    # so this is the earliest point it can run at all.
    run(
        [
            'docker',
            'run',
            '--rm',
            '--volume',
            f'{project}:/workspace',
            '--workdir',
            '/workspace',
            HADOLINT_IMAGE,
            'hadolint',
            'Dockerfile',
        ],
        cwd=project,
    )

    run(['docker', 'build', '--tag', IMAGE_TAG, '.'], cwd=project)

    try:
        result = run(
            ['docker', 'run', '--rm', '--entrypoint', 'id', IMAGE_TAG],
            cwd=project,
        )
        # The final stage must not run as root. This is what DL3066 and the
        # generated project's hadolint workflow are guarding.
        assert 'uid=0(root)' not in result.stdout, (
            f'image should not run as root, got: {result.stdout.strip()}'
        )
    finally:
        run(['docker', 'rmi', '--force', IMAGE_TAG], cwd=project, check=False)


# vim: fenc=utf-8
# vim: filetype=python
