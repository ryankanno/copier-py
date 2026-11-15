# Root workflows actions lockfile - Grilled

## Decisions
- Dependabot: no change to `.github/dependabot.yml`. Dependabot regenerates the matching `actions.lock` entry in its bump PR. The `github-actions` entry has no `automerge` label, so a person merges these PRs and sees the verify result.
- Narrowing: run `gh actions-lock` with default narrowing. Partial refs such as `actions/checkout@v7` become full tags such as `@v7.0.1`.
- Verify home: a new `.github/workflows/verify-lockfile.yml`, copied unchanged from the extension. It runs on every `pull_request` and on push to `main`, and installs the extension with `--pin v0.4.1`.
- Pre-commit: no `gh actions-lock --verify-local` hook. The verify-lockfile CI check is the only gate.
- Docs: one step in the README Contributing list: after a change to a `uses:` line or a new workflow, run `gh actions-lock` and commit what it changes in `.github/workflows/` (`actions.lock` and any rewritten `uses:` refs).
- Test: `tests/test_actions_lock.py::test_lockfile_covers_every_workflow` reads `actions.lock` by regex and asserts that its `workflows:` keys equal the files in `.github/workflows/`. A local run shows `gh actions-lock --verify` exits 0 when complete and exits 1 on an unlocked `uses:` line.
- Container images: accept the 4 `container-image` warnings (`wagoid/commitlint-github-action`, `aslafy-z/conventional-pr-title-action`, `codelytv/pr-size-labeler`, `wyrihaximus/github-action-wait-for-status`). File no follow-up issue.

## Assumptions
- [verified] Dependabot's `github-actions` updater regenerates `actions.lock` for onboarded workflows. Sources: GitHub docs "Lock workflow dependencies" ("Keep the lockfile current"), dependabot-core `github_actions/lib/dependabot/github_actions/lockfile/cli_engine.rb`, dependabot/dependabot-core#16799 (CLI v0.4.1, merged 2026-11-02), github/gh-actions-lock#257.
- [verified] The repository has no rulesets (`gh api repos/ryankanno/copier-py/rulesets` returns `[]`), so no required check changes.
- [verified] The lockfile pins action commits only. Image tags and Dockerfile `FROM` lines in the upstream action files stay mutable (github/gh-actions-lock README "Limitations", #236).
- [verified] `gh actions-lock --verify` exits 0 when only `container-image` warnings remain. Plan Task 1 Step 6 printed "All 11 workflows valid".

## Risks
- An upstream full tag moves, and verify fails until someone runs `gh actions-lock --relock`. Accepted: that failure is the purpose of the check.
- The CI pin `--pin v0.4.1` does not update by itself (github/gh-actions-lock#266). Accepted: a version bump is its own change.
- Narrowed full tags make Dependabot propose each patch release. Accepted: the `gha` group keeps it to one PR per run.

## Deferred branches
- Replacing the 4 container-image actions: outside #107.
- The template's workflows: #108.

## Next step
Ready for superpowers:executing-plans.
