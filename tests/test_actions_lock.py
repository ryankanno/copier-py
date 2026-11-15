#!/usr/bin/env python
#
# Copyright (c) 2026 Ryan Kanno <ryankanno@localkinegrinds.com>
#
# Distributed under terms of the MIT license.

"""Tests that the actions lockfile covers every root workflow.

The runner enforces the lockfile only for workflows it lists, so a
workflow added without a `gh actions-lock` run would run unlocked.
"""

import re
from pathlib import Path


WORKFLOWS_DIR = Path(__file__).parent.parent / '.github' / 'workflows'

# The `workflows:` map's quoted keys, read by regex like the other tests
# here, so PyYAML does not become a direct dependency.
WORKFLOWS_SECTION = re.compile(
    r'^workflows:\n(?P<body>(?:[ \t]+.*\n)+)', re.MULTILINE
)
WORKFLOW_KEY = re.compile(r"^[ \t]+'(?P<path>[^']+)':\s*$", re.MULTILINE)


def locked_workflows() -> set[str]:
    """The workflow paths the lockfile records."""
    text = (WORKFLOWS_DIR / 'actions.lock').read_text(encoding='utf-8')
    section = WORKFLOWS_SECTION.search(text)
    assert section, 'actions.lock has no workflows section'
    return {match['path'] for match in WORKFLOW_KEY.finditer(section['body'])}


def test_lockfile_covers_every_workflow() -> None:
    assert locked_workflows() == {
        f'.github/workflows/{path.name}'
        for path in WORKFLOWS_DIR.glob('*.y*ml')
    }
