# HISTORY.rst UTC date - Grilled

## Decisions
- UTC source: copier's `now()` global, `{{ now().strftime("%Y-%m-%d") }}`. The human chose it over `jinja2-time` and `copier-templates-extensions`.
- Scope: change only line 7 of `template/HISTORY.rst.jinja`. No new dependency. No change to `pyproject.toml` or `copier.yml`.
- Test: set `TZ` to `Etc/GMT+12` when the UTC hour is below 12, else `Etc/GMT-14`. Call `time.tzset()`. Restore both on teardown.
- Midnight race: the test accepts the UTC date from before or after the render.
- FutureWarning: the test does not assert it and does not suppress it.

## Assumptions
- [verified] Copier's `now()` returns `datetime.now(tz=timezone.utc)`. A copy under `TZ=Etc/GMT-14` rendered 2026-11-10 while the local date was 2026-11-11.
- [verified] The `strftime` filter from `jinja2_ansible_filters` uses `time.localtime()` and has no UTC option.
- [verified] The pytest configuration does not turn warnings into errors.

## Risks
- Copier removes `now()` in a future release, and line 7 then fails to render. Accepted: the human chose this option. The test detects the failure.
- Each `copier copy` prints a FutureWarning. Accepted: the human chose this option.

## Deferred branches
- None.

## Next step
Ready for superpowers:executing-plans.
