"""Controller layer — application state and keyboard event handling. No curses dependency."""

import curses
from dataclasses import dataclass, field

from model import Track
from service import CertificateService, ChallengeService, ProgressService, TrackService


@dataclass
class AppState:
    all_tracks: list[Track] = field(default_factory=list)
    visible_tracks: list[Track] = field(default_factory=list)
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
        service: TrackService,
        progress_service: ProgressService,
        challenge_service: ChallengeService,
        certificate_service: CertificateService,
    ) -> None:
        self._service = service
        self._progress = progress_service
        self._challenge = challenge_service
        self._certificate = certificate_service
        tracks = service.all()
        self.state = AppState(
            all_tracks=tracks,
            visible_tracks=list(tracks),
            in_progress_ids=progress_service.all_ids(),
            completed_ids=progress_service.all_completed_ids(),
        )

    def current_track(self) -> Track | None:
        s = self.state
        return s.visible_tracks[s.selected] if s.visible_tracks else None

    def generate_challenge(self, track: Track) -> str:
        return self._challenge.generate(track)

    def get_certificate(self, track: Track, username: str) -> tuple[list[str], bool]:
        """Return (cert_lines, from_cache).

        Loads an existing certificate if one was already issued for this track.
        Generates and persists a new one otherwise.
        """
        cached = self._certificate.load(track["id"])
        if cached is not None:
            return cached, True
        return self._certificate.generate(track, username), False

    def has_certificate(self, track_id: int) -> bool:
        """Return True if a certificate has already been issued for this track."""
        return self._certificate.load(track_id) is not None

    def toggle_progress(self) -> str:
        track = self.current_track()
        if not track:
            return ""
        msg = self._progress.toggle(track["id"])
        self._sync_progress_state()
        self.state.message = msg
        return msg

    def complete_current(self, track: Track) -> str:
        """Mark the given track as completed. Returns feedback message."""
        msg = self._progress.complete(track["id"])
        self._sync_progress_state()
        self.state.message = msg
        return msg

    def _sync_progress_state(self) -> None:
        self.state.in_progress_ids = self._progress.all_ids()
        self.state.completed_ids = self._progress.all_completed_ids()

    def apply_filter(self, query: str) -> None:
        result = self._service.search(query)
        s = self.state
        s.visible_tracks = result.tracks
        s.message = result.message
        s.selected = 0
        s.list_offset = 0

    def apply_desafio_filter(self) -> None:
        """Show only in-progress tracks. Sets message if none exist."""
        in_progress = [t for t in self.state.all_tracks if t["id"] in self.state.in_progress_ids]
        s = self.state
        if in_progress:
            s.visible_tracks = in_progress
            s.message = f"⏵ {len(in_progress)} trilha(s) em andamento."
        else:
            s.message = "Nenhuma trilha em andamento. Use Enter para iniciar uma."
        s.selected = 0
        s.list_offset = 0

    def apply_certificado_filter(self) -> None:
        """Show only completed tracks. Sets message if none exist."""
        completed = [t for t in self.state.all_tracks if t["id"] in self.state.completed_ids]
        s = self.state
        if completed:
            s.visible_tracks = completed
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
            if s.selected < len(s.visible_tracks) - 1:
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
            s.visible_tracks = list(s.all_tracks)
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
                    f"Comando desconhecido: {command}."
                    " Use /trilha [filtro], /desafio ou /certificado"
                )
            s.in_cmd_mode = False
            s.cmd_input = ""
        elif 32 <= key <= 126:
            s.cmd_input += chr(key)
        return True
