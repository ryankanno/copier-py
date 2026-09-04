#!/usr/bin/env python
#
# Copyright (c) 2026 Ryan Kanno <ryankanno@localkinegrinds.com>
#
# Distributed under terms of the MIT license.

"""Tests that README defaults match copier.yml."""

import re
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent

# Matches "- `option_name` - description (default: value)" in the README's
# template options list.
DOCUMENTED_DEFAULT = re.compile(
    r'`(?P<option>[a-z_]+)` - [^(\n]*\(default: (?P<value>[^)]+)\)'
)

# A top-level question, followed by its indented body. Read by regex rather
# than with a YAML parser, since PyYAML reaches this project only as a
# transitive dependency of copier and the tests should not be the reason it
# becomes a direct one.
QUESTION = re.compile(
    r'^(?P<name>[a-z][a-z0-9_]*):\n(?P<body>(?:[ \t]+\S.*\n)+)', re.MULTILINE
)
DEFAULT = re.compile(
    r'^\s+default:\s*"?(?P<value>[^"\n]+?)"?\s*$', re.MULTILINE
)


def copier_defaults() -> dict[str, str]:
    """The default declared for each question in copier.yml.

    Questions without a default are omitted, so a documented default for
    one is reported as a mismatch rather than passing silently.
    """
    text = (REPO_ROOT / 'copier.yml').read_text(encoding='utf-8')

    found: dict[str, str] = {}
    for question in QUESTION.finditer(text):
        default = DEFAULT.search(question['body'])
        if default:
            found[question['name']] = default['value']
    return found


def test_readme_documents_the_real_defaults() -> None:
    """Every default stated in the README matches copier.yml.

    The README restates values that live in copier.yml, so changing a
    default silently invalidates the prose. Three had drifted in the
    cookiecutter equivalent before its test existed.
    """
    readme = (REPO_ROOT / 'README.md').read_text(encoding='utf-8')
    declared = copier_defaults()

    documented = {
        match['option']: match['value']
        for match in DOCUMENTED_DEFAULT.finditer(readme)
    }
    assert documented, 'no documented defaults found; has the format changed?'

    mismatches = []
    for option, stated in documented.items():
        if option not in declared:
            mismatches.append(
                f'{option}: documented but has no default in copier.yml'
            )
            continue

        actual = declared[option]
        if actual != stated:
            mismatches.append(
                f'{option}: README says {stated!r}, actual {actual!r}'
            )

    assert not mismatches, 'README defaults are out of date:\n' + '\n'.join(
        mismatches
    )


# vim: fenc=utf-8
# vim: filetype=python
