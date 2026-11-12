# HISTORY.rst UTC date without now() - Grilled

## Decisions
- UTC source: pure Jinja with copier's default `jinja2_ansible_filters`. `strftime` renders local time with `%z`, `to_datetime` parses it, and the template subtracts `utcoffset()`. The human chose it over `copier-templates-extensions` and a post-copy task.
- Scope: in the template, change only line 7 of `template/HISTORY.rst.jinja`. No new dependency. No change to `pyproject.toml`, `copier.yml` or the lockfile.
- Comment: one Jinja comment above the expression states why the offset is subtracted.
- Warning test: a new test fails when a copy emits a warning that says `'now' will be removed`, and only that warning.
- UTC test: `test_history_date_is_utc` stays unchanged.

## Assumptions
- [verified] Copier does not add the template directory to `sys.path`, so a local `_jinja_extensions` module needs `copier-templates-extensions`.
- [verified] Under `TZ=Etc/GMT-14` at 2026-11-12 19:35 UTC, the expression rendered `2026-11-12` while the local date was 2026-11-13, with no FutureWarning.
- [unverified] `time.strftime("%z")` gives a numeric offset on Windows. To verify: run a copy on Windows. The test suite runs on macOS and Linux only.

## Risks
- `jinja2_ansible_filters` changes `strftime` or `to_datetime`. Mitigation: `test_history_date_is_utc` fails.
- On a platform where `%z` is not numeric, `to_datetime` fails and the copy stops. Accepted: no Windows test target exists.

## Deferred branches
- None.

## Next step
Ready for superpowers:executing-plans.
