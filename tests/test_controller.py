"""Tests for controller.py — AppState, Controller logic (no terminal needed)."""

from pathlib import Path

import pytest
from controller import Controller
from model import ProgressRepository, TrackRepository
from service import CertificateService, ChallengeService, ProgressService, TrackService

# curses key constants (integers — no terminal required)
KEY_DOWN = 258
KEY_UP = 259
KEY_BACKSPACE = 263
KEY_ENTER = 343
KEY_ESC = 27
KEY_Q = ord("q")
KEY_SLASH = ord("/")


# ── factory / fixture ─────────────────────────────────────────────────────────


def make_controller(tracks_json: Path, progress_json: Path, certs_dir: Path) -> Controller:
    track_svc = TrackService(TrackRepository(str(tracks_json)))
    progress_svc = ProgressService(ProgressRepository(str(progress_json)))
    challenge_svc = ChallengeService()
    cert_svc = CertificateService(str(certs_dir))
    return Controller(track_svc, progress_svc, challenge_svc, cert_svc)


@pytest.fixture()
def ctrl(tracks_json: Path, progress_json: Path, certs_dir: Path) -> Controller:
    return make_controller(tracks_json, progress_json, certs_dir)


# ── initial state ─────────────────────────────────────────────────────────────


class TestInitialState:
    def test_all_tracks_loaded(self, ctrl: Controller) -> None:
        assert len(ctrl.state.all_tracks) == 3
        assert len(ctrl.state.visible_tracks) == 3

    def test_selected_starts_at_zero(self, ctrl: Controller) -> None:
        assert ctrl.state.selected == 0

    def test_current_track_is_first(self, ctrl: Controller) -> None:
        assert ctrl.current_track() is not None
        assert ctrl.current_track()["id"] == 1  # type: ignore[index]


# ── navigation ────────────────────────────────────────────────────────────────


class TestNavigation:
    def test_down_moves_selection(self, ctrl: Controller) -> None:
        ctrl.handle_key(KEY_DOWN, visible_rows=10)
        assert ctrl.state.selected == 1

    def test_up_at_zero_stays(self, ctrl: Controller) -> None:
        ctrl.handle_key(KEY_UP, visible_rows=10)
        assert ctrl.state.selected == 0

    def test_down_then_up_returns_to_zero(self, ctrl: Controller) -> None:
        ctrl.handle_key(KEY_DOWN, visible_rows=10)
        ctrl.handle_key(KEY_UP, visible_rows=10)
        assert ctrl.state.selected == 0

    def test_cannot_go_below_last(self, ctrl: Controller) -> None:
        for _ in range(10):
            ctrl.handle_key(KEY_DOWN, visible_rows=10)
        assert ctrl.state.selected == 2  # 3 tracks, max index = 2

    def test_q_returns_false(self, ctrl: Controller) -> None:
        result = ctrl.handle_key(KEY_Q, visible_rows=10)
        assert result is False

    def test_esc_clears_filter(self, ctrl: Controller) -> None:
        ctrl.apply_filter("python")
        ctrl.handle_key(KEY_ESC, visible_rows=10)
        assert len(ctrl.state.visible_tracks) == 3

    def test_scroll_offset_increases(self, ctrl: Controller) -> None:
        # visible_rows=1 forces scroll after first down
        ctrl.handle_key(KEY_DOWN, visible_rows=1)
        assert ctrl.state.list_offset == 1

    def test_scroll_offset_decreases_on_up(self, ctrl: Controller) -> None:
        ctrl.handle_key(KEY_DOWN, visible_rows=1)
        ctrl.handle_key(KEY_UP, visible_rows=1)
        assert ctrl.state.list_offset == 0


# ── command mode ──────────────────────────────────────────────────────────────


class TestCommandMode:
    def test_slash_enters_cmd_mode(self, ctrl: Controller) -> None:
        ctrl.handle_key(KEY_SLASH, visible_rows=10)
        assert ctrl.state.in_cmd_mode is True
        assert ctrl.state.cmd_input == "/"

    def test_esc_exits_cmd_mode(self, ctrl: Controller) -> None:
        ctrl.handle_key(KEY_SLASH, visible_rows=10)
        ctrl.handle_key(KEY_ESC, visible_rows=10)
        assert ctrl.state.in_cmd_mode is False

    def test_typing_builds_cmd_input(self, ctrl: Controller) -> None:
        ctrl.handle_key(KEY_SLASH, visible_rows=10)
        for ch in "trilha":
            ctrl.handle_key(ord(ch), visible_rows=10)
        assert ctrl.state.cmd_input == "/trilha"

    def test_backspace_removes_char(self, ctrl: Controller) -> None:
        ctrl.handle_key(KEY_SLASH, visible_rows=10)
        ctrl.handle_key(ord("x"), visible_rows=10)
        ctrl.handle_key(KEY_BACKSPACE, visible_rows=10)
        assert ctrl.state.cmd_input == "/"

    def test_backspace_on_slash_exits_cmd_mode(self, ctrl: Controller) -> None:
        ctrl.handle_key(KEY_SLASH, visible_rows=10)
        ctrl.handle_key(KEY_BACKSPACE, visible_rows=10)
        assert ctrl.state.in_cmd_mode is False

    def test_enter_runs_trilha_command(self, ctrl: Controller) -> None:
        ctrl.handle_key(KEY_SLASH, visible_rows=10)
        for ch in "trilha python":
            ctrl.handle_key(ord(ch), visible_rows=10)
        ctrl.handle_key(KEY_ENTER, visible_rows=10)
        assert ctrl.state.in_cmd_mode is False
        assert all(
            "python" in t["technology"].lower() or "python" in t["name"].lower()
            for t in ctrl.state.visible_tracks
        )

    def test_enter_runs_desafio_command(self, ctrl: Controller) -> None:
        # put track 1 in progress first
        ctrl.toggle_progress()
        # now issue /desafio
        ctrl.handle_key(KEY_SLASH, visible_rows=10)
        for ch in "desafio":
            ctrl.handle_key(ord(ch), visible_rows=10)
        ctrl.handle_key(KEY_ENTER, visible_rows=10)
        assert len(ctrl.state.visible_tracks) == 1
        assert ctrl.state.visible_tracks[0]["id"] == 1

    def test_enter_unknown_command_sets_message(self, ctrl: Controller) -> None:
        ctrl.handle_key(KEY_SLASH, visible_rows=10)
        for ch in "unknown":
            ctrl.handle_key(ord(ch), visible_rows=10)
        ctrl.handle_key(KEY_ENTER, visible_rows=10)
        assert "desconhecido" in ctrl.state.message.lower()


# ── toggle_progress and complete ──────────────────────────────────────────────


class TestProgressControl:
    def test_toggle_marks_in_progress(self, ctrl: Controller) -> None:
        ctrl.toggle_progress()
        assert 1 in ctrl.state.in_progress_ids

    def test_toggle_twice_removes(self, ctrl: Controller) -> None:
        ctrl.toggle_progress()
        ctrl.toggle_progress()
        assert 1 not in ctrl.state.in_progress_ids

    def test_complete_current(self, ctrl: Controller) -> None:
        track = ctrl.current_track()
        ctrl.complete_current(track)  # type: ignore[arg-type]
        assert 1 in ctrl.state.completed_ids

    def test_toggle_on_completed_track_does_nothing(self, ctrl: Controller) -> None:
        track = ctrl.current_track()
        ctrl.complete_current(track)  # type: ignore[arg-type]
        msg = ctrl.toggle_progress()
        assert "concluída" in msg


# ── filters ───────────────────────────────────────────────────────────────────


class TestFilters:
    def test_apply_filter_reduces_visible(self, ctrl: Controller) -> None:
        ctrl.apply_filter("javascript")
        assert len(ctrl.state.visible_tracks) == 1

    def test_apply_certificado_filter_empty(self, ctrl: Controller) -> None:
        ctrl.apply_certificado_filter()
        assert "Nenhuma" in ctrl.state.message

    def test_apply_certificado_filter_with_completed(self, ctrl: Controller) -> None:
        ctrl.complete_current(ctrl.current_track())  # type: ignore[arg-type]
        ctrl.apply_certificado_filter()
        assert len(ctrl.state.visible_tracks) == 1

    def test_apply_desafio_filter_empty(self, ctrl: Controller) -> None:
        ctrl.apply_desafio_filter()
        assert "Nenhuma" in ctrl.state.message

    def test_apply_desafio_filter_with_in_progress(self, ctrl: Controller) -> None:
        ctrl.toggle_progress()
        ctrl.apply_desafio_filter()
        assert len(ctrl.state.visible_tracks) == 1


# ── get_certificate ───────────────────────────────────────────────────────────


class TestGetCertificate:
    def test_generates_new_certificate(self, ctrl: Controller) -> None:
        track = ctrl.current_track()
        lines, from_cache = ctrl.get_certificate(track, "Ana")  # type: ignore[arg-type]
        assert isinstance(lines, list)
        assert from_cache is False

    def test_loads_from_cache_on_second_call(self, ctrl: Controller) -> None:
        track = ctrl.current_track()
        ctrl.get_certificate(track, "Ana")  # type: ignore[arg-type]
        lines2, from_cache = ctrl.get_certificate(track, "Ana")  # type: ignore[arg-type]
        assert from_cache is True

    def test_has_certificate_false_before_generate(self, ctrl: Controller) -> None:
        assert ctrl.has_certificate(1) is False

    def test_has_certificate_true_after_generate(self, ctrl: Controller) -> None:
        track = ctrl.current_track()
        ctrl.get_certificate(track, "Ana")  # type: ignore[arg-type]
        assert ctrl.has_certificate(1) is True
