#!/usr/bin/env python
#
# Copyright (c) 2026 Ryan Kanno <ryankanno@localkinegrinds.com>
#
# Distributed under terms of the MIT license.

"""Tests for the exit status of scripts/parity-test.sh."""

from pathlib import Path

import pytest

from tests.test_baked_project import run


REPO_ROOT = Path(__file__).parent.parent
SCRIPT = REPO_ROOT / "scripts" / "parity-test.sh"

# The real tools render from the network (cruft clones cookiecutter-py), so
# stand-ins copy prepared trees to the destinations the script asks for.
FAKE_UVX = """#!/usr/bin/env bash
set -euo pipefail
for dest in "$@"; do :; done
mkdir -p "${dest:?}"
cp -R "${PARITY_LEFT:?}/." "${dest:?}"
"""

FAKE_UV = """#!/usr/bin/env bash
set -euo pipefail
out=""
while [[ $# -gt 0 ]]; do
    if [ "$1" = "--output-dir" ]; then
        out="$2"
    fi
    shift
done
mkdir -p "${out:?}/foobar"
cp -R "${PARITY_RIGHT:?}/." "${out:?}/foobar"
"""

DOCKERIGNORE_LEFT = ".git\n.copier-answers.yml\n.venv\n"
DOCKERIGNORE_RIGHT = ".git\n.cruft.json\n.venv\n"


def write_tree(root: Path, files: dict[str, str]) -> None:
    for name, content in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def expected_only_trees() -> tuple[dict[str, str], dict[str, str]]:
    """Two outputs whose only differences come from the two tools."""
    left = {
        ".copier-answers.yml": "_src_path: .\n",
        ".dockerignore": DOCKERIGNORE_LEFT,
        "README.md": "# Foobar\n",
    }
    right = {
        ".cruft.json": "{}\n",
        ".dockerignore": DOCKERIGNORE_RIGHT,
        "README.md": "# Foobar\n",
    }
    return left, right


def run_parity(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    left: dict[str, str],
    right: dict[str, str],
) -> tuple[int, str, str]:
    """Run the script and return its exit code, stdout, and report file."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name, body in (("uvx", FAKE_UVX), ("uv", FAKE_UV)):
        tool = bin_dir / name
        tool.write_text(body, encoding="utf-8")
        tool.chmod(0o755)

    write_tree(tmp_path / "left", left)
    write_tree(tmp_path / "right", right)
    output_dir = tmp_path / "out"

    monkeypatch.setenv("PARITY_LEFT", str(tmp_path / "left"))
    monkeypatch.setenv("PARITY_RIGHT", str(tmp_path / "right"))
    monkeypatch.setenv("PATH", str(bin_dir), prepend=":")
    result = run(
        ["bash", str(SCRIPT), "--output-dir", str(output_dir)],
        cwd=tmp_path,
        check=False,
    )
    report = (output_dir / "parity-report.txt").read_text(encoding="utf-8")
    return result.returncode, result.stdout + result.stderr, report


def result_line(report: str) -> str:
    return next(
        line for line in report.splitlines() if line.startswith("RESULT:")
    )


def test_only_expected_differences_exit_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    left, right = expected_only_trees()

    code, output, report = run_parity(tmp_path, monkeypatch, left, right)

    assert code == 0, output
    assert result_line(report) == (
        "RESULT: 0 unexpected, 3 expected difference(s) (+0 whitespace-only)"
    )
    assert "(expected)" in report


def test_whitespace_only_differences_do_not_change_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    left, right = expected_only_trees()
    left["tox.ini"] = "[tox]\nlabels =\n    test = py312\n"
    right["tox.ini"] = "[tox]\nlabels =\n  test = py312\n"

    code, output, report = run_parity(tmp_path, monkeypatch, left, right)

    assert code == 0, output
    assert result_line(report) == (
        "RESULT: 0 unexpected, 3 expected difference(s) (+1 whitespace-only)"
    )


@pytest.mark.parametrize(
    "dockerignore",
    [
        pytest.param(".git  \n.cruft.json\r\n.venv\n", id="trailing"),
        pytest.param(".git\n  .cruft.json\n.venv\n", id="leading"),
    ],
)
def test_whitespace_change_beside_expected_dockerignore_swap_exits_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, dockerignore: str
) -> None:
    left, right = expected_only_trees()
    right[".dockerignore"] = dockerignore

    code, output, report = run_parity(tmp_path, monkeypatch, left, right)

    assert code == 0, output
    assert result_line(report) == (
        "RESULT: 0 unexpected, 3 expected difference(s) (+0 whitespace-only)"
    )


@pytest.mark.parametrize(
    "change",
    [
        pytest.param({"left": {"README.md": "# Other\n"}}, id="content-diff"),
        pytest.param({"left": {"extra.txt": "x\n"}}, id="copier-only-file"),
        pytest.param(
            {"right": {"extra.txt": "x\n"}}, id="cookiecutter-only-file"
        ),
        pytest.param(
            {"left": {".dockerignore": DOCKERIGNORE_LEFT + "dist\n"}},
            id="dockerignore-extra-change",
        ),
    ],
)
def test_unexpected_difference_exits_one_after_full_report(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    change: dict[str, dict[str, str]],
) -> None:
    left, right = expected_only_trees()
    left.update(change.get("left", {}))
    right.update(change.get("right", {}))

    code, output, report = run_parity(tmp_path, monkeypatch, left, right)

    assert code == 1, output
    assert result_line(report).startswith("RESULT: 1 unexpected, ")
    assert report.rstrip().endswith("parity-report.txt")
    assert report in output


def test_help_documents_exit_one(tmp_path: Path) -> None:
    result = run(["bash", str(SCRIPT), "--help"], cwd=tmp_path)

    help_text = " ".join(result.stdout.split())
    assert "1 unexpected differences exist" in help_text
