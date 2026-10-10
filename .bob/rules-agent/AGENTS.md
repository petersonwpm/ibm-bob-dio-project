# AGENTS.md — Agent Mode

This file provides guidance to agents when working with code in this repository.

## Coding Rules (non-obvious)

- **Never use `win.refresh()`** in draw functions — use `win.noutrefresh()`. Flush with `curses.doupdate()` only via `_redraw()`.
- **`_redraw()` signature is intentionally long** — the formatter expands it one-arg-per-line. Accept it, don't refactor.
- **`DATA_PATH` uses `__file__`** — path resolution breaks if the script is run from a different cwd. Always run from project root or use `.venv/bin/python dio_explorer/src/tui.py`.
- **No test runner** — validate with `python3 -m py_compile` + `.venv/bin/ruff check` + `.venv/bin/ruff format --check`.
- **Install packages with `uv pip install --python .venv/bin/python`**, not `pip install` or `uv add` (no lockfile yet).
- **`trilha_atual` must be recomputed after each resize/fullscreen** — it's derived from `visible_trilhas[selected]` inside the loop, not stored as state.
