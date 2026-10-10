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
  src/
    tui.py          # entrypoint — wires model, service, controller, view (~60 lines)
    model.py        # Trilha TypedDict + TrilhaRepository (load only)
    service.py      # TrilhaService + SearchResult (search logic + fallback)
    controller.py   # AppState dataclass + Controller.handle_key() (no curses)
    view.py         # all curses draw functions, make_wins(), redraw()
  data/trilhas_dio.json  # trilhas data (30 entries); loaded at runtime via DATA_PATH relative to __file__
  docs/mvc-refactor.md   # improvement plan and layer contracts
  commands/         # empty (reserved)
  mcp/              # empty (reserved)
.bob/commands/      # Bob slash commands: /trilha, /desafio, /certificado
.bob/skills/        # Bob skills mirroring the commands
pyproject.toml      # ruff config lives here (line-length=100, rules E/W/F/I/B/UP)
```

## Critical Patterns

- **`noutrefresh()` + `curses.doupdate()`** — all draw functions call `win.noutrefresh()`, never `win.refresh()`. A single `curses.doupdate()` in `view.redraw()` flushes everything atomically. Breaking this causes blank screen on first load.
- **`stdscr.refresh()` must be called once before `view.redraw()`** at startup — required to flush the blank background before the first `getch()` blocks. Without it, the TUI only appears after the first keypress.
- **`view.redraw()` must be called at the end of every loop iteration** to keep display in sync with state.
- **`view.make_wins()` must be re-called after `show_fullscreen()`** — fullscreen calls `stdscr.clear()` which invalidates existing windows.
- **`safe_addstr()`** must be used instead of `win.addstr()` everywhere — guards against `curses.error` on terminal boundary.
- **Color pairs** are module-level integer constants in `view.py` (`C_NORMAL=1` … `C_CMD=8`). `curses.use_default_colors()` is called so background `-1` means terminal default.
- **`model.py` and `controller.py` must never import `curses`** — they are pure Python and must remain testable without a terminal.

## Ruff Config (non-defaults)

- `line-length = 100` (not the ruff default of 88)
- Long function signatures must be expanded one-arg-per-line by the formatter — do not fight it
- `# noqa: PLR0913` used on `_redraw()` to suppress too-many-arguments warning (PLR not in active ruleset but kept for safety)
- `UP035` enforced: use `list[...]` / `dict | None` — never `typing.List` / `typing.Optional`

## Collaboration Workflow

- Investigate the existing codebase and understand the relevant context before proposing changes.
- For tasks involving meaningful implementation decisions, present the proposed approach and relevant alternatives before modifying code.
- Explain the trade-offs of architectural decisions, new dependencies, changes to public interfaces, and non-trivial refactoring.
- Wait for explicit user approval before implementing changes that require a meaningful design decision.
- Do not interrupt the workflow for trivial implementation details that do not materially affect the design or behavior.
- If requirements are ambiguous and the ambiguity materially affects the solution, ask for clarification instead of making assumptions.
- Once the approach is approved, implement it, validate the result, and report what changed and which checks were actually executed.

## Learning and Knowledge Sharing

- Treat implementation tasks as opportunities for learning, not merely code delivery.
- When a solution introduces an unfamiliar or non-trivial concept, explain what it is, why it is relevant, and how it works in the current context.
- Present meaningful alternatives when they offer different trade-offs in readability, maintainability, performance, or complexity.
- Do not avoid advanced language features, design patterns, or abstractions solely because they may be unfamiliar.
- Prefer explicit, idiomatic Python, and explain when a more sophisticated approach offers a concrete advantage.
- Relate explanations to the existing code whenever possible, using small examples rather than generic lectures.
- Distinguish between what is required to solve the problem and what is an optional improvement or learning opportunity.
- Let the user decide whether to adopt optional improvements that materially change the implementation.

## Scope Control

- Keep changes limited to the requested task and its necessary consequences.
- Do not perform unrelated refactoring, cleanup, renaming, or formatting changes.
- If investigation reveals other defects or improvement opportunities, report them separately without modifying the affected code.
- Include adjacent changes only when they are necessary for correctness or explicitly approved by the user.
- Avoid introducing new abstractions or dependencies outside the approved scope.

## Writing Style

- Use plain, clear, and concise English in all project artifacts.
- Prefer common words and direct sentences over sophisticated vocabulary, jargon, or unnecessarily formal expressions.
- Prefer active voice and straightforward phrasing.
- Explain technical concepts precisely without making the explanation more complex than necessary.
- Use technical terminology when it improves accuracy; avoid jargon when a simpler term works.
- Avoid verbosity, filler phrases, corporate language, and redundant explanations.
- Write for a technically experienced developer who values clarity over elaborate prose.
