# Root Workflows Actions Lockfile Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pin every action that the root workflows use in `.github/workflows/actions.lock`, and fail CI when a `uses:` line has no lockfile entry.

**Architecture:** `gh actions-lock` (v0.4.1, installed on the host) writes the lockfile. A new workflow, copied from the extension's `verify-lockfile.yml`, runs `gh actions-lock --verify` in CI. A pytest test checks offline that the lockfile names every root workflow.

**Tech Stack:** `gh` + `gh-actions-lock` v0.4.1, GitHub Actions, pytest (stdlib only).

**Spec:** issue ryankanno/copier-py#107. Decisions: `docs/plans/2026-11-14-actions-lockfile-grilled.md`.

## Global Constraints

- No `--verify-local` pre-commit hook, and no change to `.github/dependabot.yml`.
- Change only the root `.github/` tree, its docs, and the tests. The template's workflows stay unchanged.
- No change to `pyproject.toml` or `uv.lock`.
- No skipped tests, no lowered checks.
- The host already has the `gh-actions-lock` v0.4.1 extension. Do not install, upgrade or remove any `gh` extension on the host.
- The CI job installs the extension with `--pin v0.4.1`.

## Review Focus

- A new workflow file added later without a lockfile run: `test_lockfile_covers_every_workflow` fails, and CI verify fails.
- A Dependabot `github-actions` bump: Dependabot regenerates the lockfile entry in the same PR (GitHub docs, "Keep the lockfile current"). The verify job passes.
- A workflow with only `container-image` warnings: `--verify` exits 0. Task 1 Step 6 checks this.
- The verify job on a Dependabot PR has a read-only `GITHUB_TOKEN`. The job needs only `contents: read`.
- An upstream full tag that moves: `--verify` reports an error until a person runs `gh actions-lock --relock`.

---

### Task 1: Lock the root workflows and verify the lockfile in CI

**Files:**
- Create: `tests/test_actions_lock.py`
- Create: `.github/workflows/verify-lockfile.yml`
- Create: `.github/workflows/actions.lock` (written by the tool)
- Modify: `.github/workflows/*.yml` `uses:` lines (written by the tool, when refs are narrowed)

**Interfaces:**
- Produces: `.github/workflows/actions.lock` with a top-level `workflows:` map keyed by `'.github/workflows/<name>.yml'`.

- [ ] **Step 1: Write the failing test**

`tests/test_actions_lock.py::test_lockfile_covers_every_workflow`: read `actions.lock` as text. Take the quoted keys under `workflows:` by regex (no YAML dependency, as `tests/test_version_consistency.py` does). Assert that the set equals `{'.github/workflows/' + p.name for p in WORKFLOWS_DIR.glob('*.y*ml')}`.

- [ ] **Step 2: Run it and see it fail**

Run: `just tests -- tests/test_actions_lock.py`
Expected: FAIL, `FileNotFoundError` for `actions.lock`.

- [ ] **Step 3: Add `.github/workflows/verify-lockfile.yml`**

Copy the extension's `verify-lockfile.yml` verbatim: triggers `pull_request` and `push` to `main`, `permissions: contents: read`, `GH_TOKEN: ${{ github.token }}`, checkout with `persist-credentials: false`, `gh extension install github/gh-actions-lock --pin v0.4.1`, `gh actions-lock --verify`.

- [ ] **Step 4: Run `gh actions-lock` from the worktree root**

Run: `gh actions-lock` (default ref narrowing).
Expected: exit 0. It writes `actions.lock` and rewrites partial refs such as `@v7` to full tags.

- [ ] **Step 5: Run the test and see it pass**

Run: `just tests -- tests/test_actions_lock.py`
Expected: PASS.

- [ ] **Step 6: Run the CI check locally**

Run: `gh actions-lock --verify`
Expected: exit 0. The four `container-image` warnings stay.

- [ ] **Step 7: Show that verify fails on an unlocked `uses:` line**

Add `- uses: actions/hello-world-javascript-action@v1` to a copy of a step in `trufflehog.yml`. Run `gh actions-lock --verify`. Expected: exit 1 with a `not-pinned` finding. Then delete only that line. Do not use `git checkout --` on the file: that also discards the Step 4 ref rewrites.

- [ ] **Step 8: Commit**

```bash
git add tests/test_actions_lock.py .github/workflows
git commit -m "ci: lock the root workflows' actions with gh-actions-lock"
```

### Task 2: Document the lock step

**Files:**
- Modify: `README.md` (Contributing section)

- [ ] **Step 1: Add the step**

Add one step to the Contributing list: after a change to a `uses:` line or a new workflow, run `gh actions-lock` and commit what it changes in `.github/workflows/` (`actions.lock` and any rewritten `uses:` refs). Link the extension's install section.

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: document the gh actions-lock step for workflow changes"
```
