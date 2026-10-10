"""Controller layer — application state and keyboard event handling. No curses dependency."""

import curses
from dataclasses import dataclass, field

from model import Trilha, TrilhaRepository


@dataclass
class AppState:
    all_trilhas: list[Trilha] = field(default_factory=list)
    visible_trilhas: list[Trilha] = field(default_factory=list)
    selected: int = 0
    list_offset: int = 0
    cmd_input: str = ""
    in_cmd_mode: bool = False
    message: str = ""
    prompt: str = "▶ "


class Controller:
    def __init__(self, repo: TrilhaRepository) -> None:
        self._repo = repo
        self.state = AppState(
            all_trilhas=repo.all(),
            visible_trilhas=repo.all(),
        )

    def apply_filter(self, query: str) -> None:
        results = self._repo.search(query)
        s = self.state
        if results:
            s.visible_trilhas = results
            s.message = f"✔ {len(results)} trilha(s) encontrada(s)."
        else:
            s.visible_trilhas = list(s.all_trilhas)
            s.message = "✘ Nenhuma trilha encontrada. Mostrando todas."
        s.selected = 0
        s.list_offset = 0

    def handle_key(self, key: int, visible_rows: int) -> bool:
        """Process one keypress. Returns False when the app should quit."""
        s = self.state
        s.message = ""

        if not s.in_cmd_mode:
            return self._handle_nav(key, visible_rows)
        else:
            return self._handle_cmd(key)

    def _handle_nav(self, key: int, visible_rows: int) -> bool:
        s = self.state
        if key in (ord("q"), ord("Q")):
            return False
        elif key == curses.KEY_DOWN:
            if s.selected < len(s.visible_trilhas) - 1:
                s.selected += 1
                if s.selected >= s.list_offset + visible_rows:
                    s.list_offset += 1
        elif key == curses.KEY_UP:
            if s.selected > 0:
                s.selected -= 1
                if s.selected < s.list_offset:
                    s.list_offset -= 1
        elif key == ord("/"):
            s.in_cmd_mode = True
            s.cmd_input = "/"
        elif key == 27:  # ESC — clear filter
            s.visible_trilhas = list(s.all_trilhas)
            s.selected = 0
            s.list_offset = 0
            s.cmd_input = ""
        return True

    def _handle_cmd(self, key: int) -> bool:
        s = self.state
        if key == 27:  # ESC
            s.in_cmd_mode = False
            s.cmd_input = ""
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            if len(s.cmd_input) > 1:
                s.cmd_input = s.cmd_input[:-1]
            else:
                s.in_cmd_mode = False
                s.cmd_input = ""
        elif key in (ord("\n"), curses.KEY_ENTER):
            parts = s.cmd_input.strip().split(None, 1)
            command = parts[0].lower() if parts else ""
            arg = parts[1] if len(parts) > 1 else ""
            if command == "/trilha":
                self.apply_filter(arg)
            else:
                s.message = f"Unknown command: {command}. Use /trilha [filter]"
            s.in_cmd_mode = False
            s.cmd_input = ""
        elif 32 <= key <= 126:
            s.cmd_input += chr(key)
        return True
