# HISTORY.rst UTC Date Without now() Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render the UTC date in the generated `HISTORY.rst` without copier's deprecated `now()` global.

**Architecture:** Copier loads `jinja2_ansible_filters` by default. Its `strftime` filter renders the local time with the `%z` offset. Its `to_datetime` filter parses that string into an aware `datetime`. Subtracting `utcoffset()` gives the UTC wall time. Only `template/HISTORY.rst.jinja` line 7 changes.

**Tech Stack:** copier 9.19.1, Jinja2 sandbox, `jinja2_ansible_filters` (a copier dependency), pytest.

**Spec:** GitHub issue ryankanno/copier-py#104. Grilled decisions: `docs/plans/2026-11-12-history-rst-date-without-now-grilled.md`.

## Global Constraints

- The generated `HISTORY.rst` shows the UTC date, without copier's `now()` global.
- A `copier copy` of the template prints no `'now' will be removed` FutureWarning.
- `test_history_date_is_utc` passes, unchanged in what it asserts.
- No new dependency. No change to `pyproject.toml`, `copier.yml` or the lockfile, unless the grill approves it.
- No skipped or xfailed tests. No warning filters that hide the FutureWarning.

## Verified facts

- [verified] Copier does not add the template directory to `sys.path` (`copier/_main.py` `jinja_env`). A local extension in `_jinja_extensions` needs `copier-templates-extensions` to import.
- [verified] `jinja2_ansible_filters.strftime(fmt)` returns `time.strftime(fmt, time.localtime())`. `to_datetime(s, fmt)` returns `datetime.strptime(s, fmt)`.
- [verified] A scratch template with the expression below, copied under `TZ=Etc/GMT-14` at 2026-11-12 19:35 UTC, rendered `local=2026-11-13 09:35:34+14:00 utc=2026-11-12` and printed no FutureWarning.

## Review Focus

- A local zone ahead of UTC (`Etc/GMT-14`): the date is the UTC date. `test_history_date_is_utc` covers it after noon UTC.
- A local zone behind UTC (`Etc/GMT+12`): the date is the UTC date. `test_history_date_is_utc` covers it before noon UTC.
- A copy under UTC itself (`+0000`): `utcoffset()` is zero and the date is unchanged. The default test environment covers it.
- A render near midnight UTC: the existing test accepts the date before or after the render.
- The FutureWarning: Task 1 adds a test that fails while `now()` is in use.

---

### Task 1: Render the UTC date without now()

**Files:**
- Modify: `template/HISTORY.rst.jinja:7`
- Test: `tests/test_copier_generation.py` (new test after `test_history_date_is_utc`)

**Interfaces:**
- Consumes: `generate_project(tmp_path: Path, data: dict[str, str | bool]) -> Path` and the `default_context` fixture.

- [ ] **Step 1: Write the failing test**

```python
def test_generation_emits_no_now_deprecation(
    tmp_path: Path, default_context: dict[str, str | bool]
) -> None:
    """Test copier copy does not call copier's deprecated now() global."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        generate_project(tmp_path, default_context)
    messages = [str(w.message) for w in caught]
    assert not [m for m in messages if "'now' will be removed" in m]
```

Add `import warnings` to the imports.

- [ ] **Step 2: Run it to verify it fails**

Run: `just tests -- tests/test_copier_generation.py::test_generation_emits_no_now_deprecation`
Expected: FAIL, the list holds the `'now' will be removed` message.

- [ ] **Step 3: Replace line 7 of `template/HISTORY.rst.jinja`**

```jinja
{# strftime alone renders the local date; subtract the offset for UTC. -#}
{% set local = "%Y-%m-%dT%H:%M:%S%z" | strftime | to_datetime("%Y-%m-%dT%H:%M:%S%z") -%}
{{ version }} - {{ (local - local.utcoffset()).strftime("%Y-%m-%d") }}
```

The rendered file must keep the same lines as before (a blank line 6, the heading on line 7).

- [ ] **Step 4: Run both tests to verify they pass**

Run: `just tests -- tests/test_copier_generation.py -k "history_date_is_utc or no_now_deprecation"`
Expected: PASS for both.

- [ ] **Step 5: Run the gate, then commit**

```bash
git add template/HISTORY.rst.jinja tests/test_copier_generation.py docs/plans/
git commit -m "fix(template): render the HISTORY.rst date without copier's now()"
```
