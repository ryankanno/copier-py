# HISTORY.rst UTC Date Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The generated `HISTORY.rst` shows the UTC date, as cookiecutter-py does.

**Architecture:** Change the date expression on line 7 of `template/HISTORY.rst.jinja`. Add one generation test that runs `run_copy` under a time zone where the local date and the UTC date differ now.

**Tech Stack:** copier `run_copy`, pytest, stdlib `time.tzset` and `datetime`.

**Spec:** ryankanno/copier-py#96

## Facts

- The current filter `strftime` comes from `jinja2_ansible_filters`. It calls `time.localtime()` and has no UTC option.
- Copier exposes a global `now()` that returns `datetime.now(tz=timezone.utc)`. Each call emits a `FutureWarning`: "'now' will be removed in a future release of Copier."
- `jinja2-time` is not in `uv.lock`.
- The pytest configuration does not turn warnings into errors.

## Decisions (from the grill)

The human confirmed these decisions on 2026-11-11.

- Line 7 becomes `{{ version }} - {{ now().strftime("%Y-%m-%d") }}`. Copier's `now()` returns the UTC time. Each copy prints copier's FutureWarning; the human accepts it.
- No new dependency. No change to `pyproject.toml`, `copier.yml`, or any other template file.
- The test sets a real `TZ` and calls `time.tzset()`. It uses no mocks and no time-freezing dependency. It does not assert or suppress the FutureWarning.

## Global Constraints

- Change no template file other than `template/HISTORY.rst.jinja`.
- No new dependency and no `pyproject.toml` change without the human's approval.

## Review Focus

- The test runs at any UTC hour. It picks UTC-12 when the UTC hour is below 12, and UTC+14 otherwise. Either zone gives a local date that differs from the UTC date.
- The test restores `TZ` and calls `time.tzset()` on teardown, so other tests in the same xdist worker see the original zone.
- A run that crosses UTC midnight during generation accepts the UTC date from before or after the render.

---

### Task 1: Render the HISTORY.rst date in UTC

**Files:**
- Modify: `template/HISTORY.rst.jinja:7`
- Test: `tests/test_copier_generation.py`

- [ ] **Step 1: Write the failing test** `test_history_date_is_utc(tmp_path, default_context, monkeypatch)`.
  Set `TZ` to `Etc/GMT+12` when the UTC hour is below 12, else `Etc/GMT-14`, then call `time.tzset()`.
  Assert the local date differs from the UTC date (proves the condition).
  Generate with `run_copy`. Assert the line `0.0.1 - <UTC date>` is in `HISTORY.rst`, for the UTC date from before or after the render.
  On teardown, restore `TZ` and call `time.tzset()`.
- [ ] **Step 2: Run** `just tests -- tests/test_copier_generation.py -k history_date_is_utc`. Expected: FAIL, the file holds the local date.
- [ ] **Step 3: Change line 7** to `{{ version }} - {{ now().strftime("%Y-%m-%d") }}`.
- [ ] **Step 4: Run** the same command. Expected: PASS.
- [ ] **Step 5: Commit** `fix(template): render the HISTORY.rst date in UTC`.
