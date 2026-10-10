"""Controller layer — application state and keyboard event handling. No curses dependency."""

import curses
from dataclasses import dataclass, field

from model import Trilha
from service import CertificateService, ChallengeService, ProgressService, TrilhaService


@dataclass
class AppState:
    all_trilhas: list[Trilha] = field(default_factory=list)
    visible_trilhas: list[Trilha] = field(default_factory=list)
    in_progress_ids: set[int] = field(default_factory=set)
    completed_ids: set[int] = field(default_factory=set)
    selected: int = 0
    list_offset: int = 0
    cmd_input: str = ""
    in_cmd_mode: bool = False
    message: str = ""
    prompt: str = "▶ "


class Controller:
    def __init__(
        self,
        service: TrilhaService,
        progress_service: ProgressService,
        challenge_service: ChallengeService,
        certificate_service: CertificateService,
    ) -> None:
        self._service = service
        self._progress = progress_service
        self._challenge = challenge_service
        self._certificate = certificate_service
        trilhas = service.all()
        self.state = AppState(
            all_trilhas=trilhas,
            visible_trilhas=list(trilhas),
            in_progress_ids=progress_service.all_ids(),
            completed_ids=progress_service.all_completed_ids(),
        )

    def current_trilha(self) -> Trilha | None:
        s = self.state
        return s.visible_trilhas[s.selected] if s.visible_trilhas else None

    def generate_challenge(self, trilha: Trilha) -> str:
        return self._challenge.generate(trilha)

    def get_certificate(self, trilha: Trilha, username: str) -> tuple[list[str], bool]:
        """Return (cert_lines, from_cache).

        Loads an existing certificate if one was already issued for this trilha.
        Generates and persists a new one otherwise.
        """
        cached = self._certificate.load(trilha["id"])
        if cached is not None:
            return cached, True
        return self._certificate.generate(trilha, username), False

    def has_certificate(self, trilha_id: int) -> bool:
        """Return True if a certificate has already been issued for this trilha."""
        return self._certificate.load(trilha_id) is not None

    def toggle_progress(self) -> str:
        trilha = self.current_trilha()
        if not trilha:
            return ""
        msg = self._progress.toggle(trilha["id"])
        self._sync_progress_state()
        self.state.message = msg
        return msg

    def complete_current(self, trilha: Trilha) -> str:
        """Mark the given trilha as completed. Returns feedback message."""
        msg = self._progress.complete(trilha["id"])
        self._sync_progress_state()
        self.state.message = msg
        return msg

    def _sync_progress_state(self) -> None:
        self.state.in_progress_ids = self._progress.all_ids()
        self.state.completed_ids = self._progress.all_completed_ids()

    def apply_filter(self, query: str) -> None:
        result = self._service.search(query)
        s = self.state
        s.visible_trilhas = result.trilhas
        s.message = result.message
        s.selected = 0
        s.list_offset = 0

    def apply_desafio_filter(self) -> None:
        """Show only in-progress trilhas. Sets message if none exist."""
        in_progress = [t for t in self.state.all_trilhas if t["id"] in self.state.in_progress_ids]
        s = self.state
        if in_progress:
            s.visible_trilhas = in_progress
            s.message = f"⏵ {len(in_progress)} trilha(s) em andamento."
        else:
            s.message = "Nenhuma trilha em andamento. Use Enter para iniciar uma."
        s.selected = 0
        s.list_offset = 0

    def apply_certificado_filter(self) -> None:
        """Show only completed trilhas. Sets message if none exist."""
        completed = [t for t in self.state.all_trilhas if t["id"] in self.state.completed_ids]
        s = self.state
        if completed:
            s.visible_trilhas = completed
            s.message = f"🏆 {len(completed)} trilha(s) concluída(s)."
        else:
            s.message = "Nenhuma trilha concluída ainda. Complete um desafio primeiro."
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
            elif command == "/desafio":
                self.apply_desafio_filter()
            elif command == "/certificado":
                self.apply_certificado_filter()
            else:
                s.message = (
                    f"Unknown command: {command}. Use /trilha [filter], /desafio or /certificado"
                )
            s.in_cmd_mode = False
            s.cmd_input = ""
        elif 32 <= key <= 126:
            s.cmd_input += chr(key)
        return True
