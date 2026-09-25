# Whose Turn? — project notes for Claude

A kid-friendly Flet (Python) app that picks a turn order, a winner or a loser from a list of players. Android first; iOS maybe later.

The owner is comfortable with Python but new to GUI/mobile dev: briefly explain notable design decisions (a few sentences, not essays).

## Environment (do not change without asking)

- macOS (Apple Silicon). Target: Android.
- **uv 0.12.x** for everything: `uv add`, `uv add --dev`, `uv run …`. Never pip, never activate venvs manually.
- **Flet 1.0.1**, pinned.
- `pyproject.toml`:
  - `requires-python = ">=3.12,<3.13"`: also decides which Python `flet build` bundles into the APK. Keep it on 3.12.
  - `[project].dependencies = ["flet==1.0.1"]` is **runtime only**. Everything here gets packaged into the APK.
  - `[dependency-groups].dev` holds dev tooling (`flet[all]==1.0.1`, `pytest`). **Never put `flet[all]` or any dev-only package in `[project].dependencies`**: e.g. `watchdog` has no Android wheels and breaks `flet build`.
  - `[tool.flet]`: `org = "com.rjsloane"`, `product = "Whose Turn?"`, `[tool.flet.app] path = "src"`.
- Flat layout (`uv init --no-package`, no build-system). Entry point: `src/main.py`.

## Commands

- Desktop: `uv run flet run src/main.py`
- Phone via the Flet app: `uv run flet run --android src/main.py`
- Build APK: `uv run flet build apk -v`
- Tests: `uv run pytest`

## Flet 1.0 gotchas

Flet 1.0 broke a lot of 0.x APIs, and much online material is outdated.

- `ft.run(main)`, not `ft.app(target=main)`.
- `ft.ElevatedButton` is gone; use `ft.Button` (or `ft.FilledButton`, `ft.TextButton`, `ft.IconButton`).
- Dialogs: `page.show_dialog(dlg)` / `page.pop_dialog()` (no `page.open()` / `dlg.open = True`).
- `TextField` inline error is the `error` property (not `error_text`).
- `control.focus()` is a coroutine: call it from an `async def` handler with `await`.
- Call `page.update()` (or `control.update()`) after changing state in event handlers.
- **Verify any control/property/service you're not certain about before using it**: check https://docs.flet.dev or introspect, e.g.
  `uv run python -c "import flet as ft, inspect; print(inspect.signature(ft.TextField.__init__))"`. Don't guess API names.

## Architecture & conventions

- **Logic separate from UI.** Pure-Python modules (no Flet imports) hold data and logic so they're unit-testable:
  - `src/models.py`: `Player` dataclass, `Roster` (add/remove with validation), mode types.
  - `src/picker.py`: pure pick functions; accept an optional `random.Random` for deterministic tests.
  - `src/storage.py`: persistence, behind a small interface so it can be swapped.
- UI lives in `src/views/` (one module per screen); `src/main.py` only does app setup.
- **State-driven UI:** state lives in plain Python objects; views re-render controls from state after every change. Controls are never the source of truth.
- Tests in `tests/`, `pythonpath = ["src"]` in `[tool.pytest.ini_options]`. Test all logic in `models.py` and `picker.py`.
- **Kid-friendly UI:** big tap targets (≥ 48 px, main buttons ~56 px+), large text, simple screens, clear feedback. Must work well in phone portrait.
- Type hints throughout; small functions.
- Future features to keep easy (see `ROADMAP.md` once written): player photos/avatars (`Player.photo_path` / `Player.avatar` already exist), built-in avatars, player groups, Play Store / iOS publishing.

## Workflow

- Work in phases; after each: run tests, confirm the desktop app launches, then stop with a summary and a phone test checklist.
- **Never run git commands that change the repo** (no add/commit/push/reset/etc.). The owner handles all git operations. Suggest a commit message instead.
