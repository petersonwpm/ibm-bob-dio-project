# AGENTS.md — Ask Mode

This file provides guidance to agents when working with code in this repository.

## Context

- The `.bob/commands/` slash commands (`/trilha`, `/desafio`, `/certificado`) read `dio_explorer/data/trilhas_dio.json` at LLM time — they are Bob prompt templates, not Python code.
- `dio_explorer/commands/`, `dio_explorer/mcp/`, `dio_explorer/docs/` are **empty directories** — reserved for future use, not currently functional.
- The TUI (`tui.py`) and the Bob slash commands are **independent** — the TUI is a standalone Python app; the slash commands are Bob prompt templates that also reference the same JSON.
- There is **no HTTP server, no API, no tests** — the project is a single-file curses TUI + Bob prompt tools.
