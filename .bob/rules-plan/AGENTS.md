# AGENTS.md — Plan Mode

This file provides guidance to agents when working with code in this repository.

## Architectural Constraints

- **Single source file** (`dio_explorer/src/tui.py`) — no modules, no packages. All logic is intentionally flat.
- **curses windowing model**: three persistent windows (`list_win`, `detail_win`, `cmd_win`) created via `_make_wins()`. They must be recreated (not resized) after terminal resize or fullscreen return — curses windows cannot be resized in place.
- **Draw pipeline is strictly one-way**: `draw_*()` → `noutrefresh()` → `_redraw()` → `doupdate()`. Any shortcut that calls `refresh()` directly breaks the atomic paint.
- **Data is read-only at runtime** — `trilhas_dio.json` is loaded once on startup. No writes, no cache invalidation needed.
- **No dependency on external packages** — only stdlib (`curses`, `json`, `os`). Adding dependencies requires `uv pip install` + updating `pyproject.toml`.
- **Bob slash commands and the TUI are separate systems** sharing the same JSON file — changes to the JSON schema affect both.
