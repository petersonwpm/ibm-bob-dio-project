# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Stack

- **Python 3.12** — `requires-python = ">=3.12"` enforced in `pyproject.toml`
- **uv** for venv and package management (not pip directly)
- **ruff** for lint + format (installed in `.venv/`, not system)

## Commands

```bash
# Run TUI
.venv/bin/python dio_explorer/src/tui.py

# Lint
.venv/bin/ruff check dio_explorer/

# Format check
.venv/bin/ruff format --check dio_explorer/

# Fix + format (apply)
.venv/bin/ruff check --fix dio_explorer/ && .venv/bin/ruff format dio_explorer/

# Add a package
uv pip install --python .venv/bin/python <package>
```

No test suite exists yet.

## Project Structure

```
dio_explorer/
  src/tui.py          # sole Python source — curses TUI entry point
  data/trilhas_dio.json  # trilhas data (30 entries); loaded at runtime via DATA_PATH relative to __file__
  commands/           # empty (reserved)
  mcp/                # empty (reserved)
.bob/commands/        # Bob slash commands: /trilha, /desafio, /certificado
.bob/skills/          # Bob skills mirroring the commands
pyproject.toml        # ruff config lives here (line-length=100, rules E/W/F/I/B/UP)
```

## Critical Patterns in tui.py

- **`noutrefresh()` + `curses.doupdate()`** — all draw functions call `win.noutrefresh()`, never `win.refresh()`. A single `curses.doupdate()` in `_redraw()` flushes everything atomically. Breaking this causes blank screen on first load.
- **`_redraw()` must be called once before the event loop** and once at the end of every loop iteration. Omitting either causes display lag.
- **`_make_wins()` must be re-called after `show_fullscreen()`** — fullscreen calls `stdscr.clear()` which invalidates existing windows.
- **`safe_addstr()`** must be used instead of `win.addstr()` everywhere — guards against `curses.error` on terminal boundary.
- **Color pairs** are module-level integer constants (`C_NORMAL=1` … `C_CMD=8`). `curses.use_default_colors()` is called so background `-1` means terminal default.

## Ruff Config (non-defaults)

- `line-length = 100` (not the ruff default of 88)
- Long function signatures must be expanded one-arg-per-line by the formatter — do not fight it
- `# noqa: PLR0913` used on `_redraw()` to suppress too-many-arguments warning (PLR not in active ruleset but kept for safety)
- `UP035` enforced: use `list[...]` / `dict | None` — never `typing.List` / `typing.Optional`
