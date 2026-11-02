#!/usr/bin/env python
#
# Copyright (c) 2026 Ryan Kanno <ryankanno@localkinegrinds.com>
#
# Distributed under terms of the MIT license.

"""Tests that README defaults match copier.yml."""

import re
from pathlib import Path

from tests.test_version_consistency import copier_default


REPO_ROOT = Path(__file__).parent.parent

# Matches "- `option_name` - description (default: value)" in the README's
# template options list.
DOCUMENTED_DEFAULT = re.compile(
    r"`(?P<option>[a-z_]+)` - [^\n]*?\(default: (?P<value>[^)]+)\)"
)


def test_readme_documents_the_real_defaults() -> None:
    """Every default stated in the README matches copier.yml.

    The README restates values that live in copier.yml, so changing a
    default silently invalidates the prose.
    """
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    documented = {
        match["option"]: match["value"]
        for match in DOCUMENTED_DEFAULT.finditer(readme)
    }
    assert documented, "no documented defaults found; has the format changed?"

    mismatches = [
        f"{option}: README says {stated!r}, actual {actual!r}"
        for option, stated in documented.items()
        if (actual := copier_default(option)) != stated
    ]

    assert not mismatches, "README defaults are out of date:\n" + "\n".join(
        mismatches
    )


# vim: fenc=utf-8
# vim: filetype=python
