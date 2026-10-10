# MVC Refactor Plan

## Context

`dio_explorer/src/tui.py` is a single 414-line file that mixes three concerns:

| Layer | Current functions |
|---|---|
| Model (data / business logic) | `load_trilhas()`, `filter_trilhas()` |
| View (curses rendering) | `draw_list()`, `draw_detail()`, `draw_cmdbar()`, `draw_hline()`, `safe_addstr()`, `show_fullscreen()`, `init_colors()` |
| Controller (app state + event loop) | `main()`, `_make_wins()`, `_redraw()`, `run()` |

The goal is to separate these concerns so that the Model and Controller are testable without `curses`.

## Target Structure

```
dio_explorer/
  src/
    model.py        # Model — pure data, no curses
    view.py         # View  — curses rendering only, no app state
    controller.py   # Controller — AppState + handle_key(), no curses calls
    tui.py          # Entrypoint — ~30 lines, wires the three layers
  tests/
    test_model.py
    test_controller.py
```

## Design Decisions

- **`Trilha` type:** `TypedDict` — zero overhead, loads directly from JSON, no conversion needed.
- **`Controller`:** class with an `AppState` dataclass attribute — easy to instantiate and inspect in tests.

## Layer Contracts

### `model.py`

- `class Trilha(TypedDict)` — mirrors the JSON schema exactly.
- `class TrilhaRepository` — `load(path)` and `search(query) -> list[Trilha]`.
- Zero `import curses`. Fully unit-testable.

### `view.py`

- All current draw functions, unchanged in behavior.
- Receives data as parameters only — no access to global app state.
- `make_wins(h, w)` (public rename of `_make_wins`).

### `controller.py`

- `@dataclass class AppState` — holds `all_trilhas`, `visible_trilhas`, `selected`, `list_offset`,
  `cmd_input`, `in_cmd_mode`, `message`, `prompt`.
- `class Controller` — `__init__(repo)`, `handle_key(key: int) -> bool` (False = quit),
  `apply_filter(query)`.
- `handle_key()` mutates `AppState` only — no `curses` calls whatsoever.

### `tui.py` (entrypoint)

```python
def main(stdscr):
    view.init_colors()
    repo = TrilhaRepository(DATA_PATH)
    ctrl = Controller(repo)
    wins = view.make_wins(*stdscr.getmaxyx())
    view.redraw(wins, ctrl.state)
    while True:
        key = stdscr.getch()
        if not ctrl.handle_key(key):
            break
        # resize handling ...
        view.redraw(wins, ctrl.state)
```

## Tests to Write (no curses mock needed)

| Test | Module | What it covers |
|---|---|---|
| `test_load_trilhas` | model | JSON loads, required fields exist |
| `test_search_by_name` | model | `search("python")` returns matching entries |
| `test_search_empty_query` | model | empty query returns all entries |
| `test_search_no_match` | model | non-matching query returns `[]` |
| `test_key_down_moves_selection` | controller | `KEY_DOWN` increments `selected` |
| `test_key_q_returns_false` | controller | `ord("q")` returns `False` |
| `test_slash_enters_cmd_mode` | controller | `ord("/")` sets `in_cmd_mode=True` |
| `test_filter_command` | controller | `/trilha python` filters correctly |
| `test_esc_clears_filter` | controller | ESC restores full list |

## Implementation Steps

1. Create `model.py` — `Trilha` TypedDict + `TrilhaRepository`.
2. Create `controller.py` — `AppState` dataclass + `Controller`.
3. Create `view.py` — move all draw functions and `init_colors` verbatim.
4. Rewrite `tui.py` as a thin entrypoint that wires the three modules.
5. Add `pytest` to dependencies (`uv pip install --python .venv/bin/python pytest`).
6. Write `tests/test_model.py` and `tests/test_controller.py`.
7. Add test command to `AGENTS.md`.
