"""Tests for the MCP server tool functions in dio_explorer/mcp/server.py.

The server uses module-level service singletons. Each test class injects
fresh instances backed by tmp_path via monkeypatch so tests are isolated.
"""

import importlib
import sys
from pathlib import Path

import pytest
from conftest import SAMPLE_TRACKS
from model import ProgressRepository, TrackRepository
from service import CertificateService, ChallengeService, ProgressService, TrackService

# ── inject server module into sys.path and import ────────────────────────────

MCP_DIR = Path(__file__).parent.parent / "dio_explorer" / "mcp"


def _import_server():
    """Import (or return cached) the mcp server module."""
    if "server" in sys.modules:
        return sys.modules["server"]
    sys.path.insert(0, str(MCP_DIR))
    # The server imports from model/service via sys.path set in its own
    # module header — those paths are already set by pytest (pythonpath config).
    # We need to prevent it from running asyncio.run at import time; it doesn't.
    return importlib.import_module("server")


# ── fixture: patch server singletons ─────────────────────────────────────────


@pytest.fixture()
def server(tracks_json: Path, progress_json: Path, certs_dir: Path, monkeypatch):
    """Return the server module with its singletons replaced by tmp instances."""
    mod = _import_server()

    track_repo = TrackRepository(str(tracks_json))
    track_svc = TrackService(track_repo)

    progress_repo = ProgressRepository(str(progress_json))
    progress_svc = ProgressService(progress_repo)

    challenge_svc = ChallengeService()
    cert_svc = CertificateService(str(certs_dir))

    monkeypatch.setattr(mod, "_track_svc", track_svc)
    monkeypatch.setattr(mod, "_progress_svc", progress_svc)
    monkeypatch.setattr(mod, "_challenge_svc", challenge_svc)
    monkeypatch.setattr(mod, "_certificate_svc", cert_svc)

    return mod


# ── list_tracks ───────────────────────────────────────────────────────────────


class TestListTracks:
    def test_no_query_returns_all(self, server) -> None:
        result = server.list_tracks()
        assert len(result) == 3

    def test_query_filters_by_technology(self, server) -> None:
        result = server.list_tracks(query="javascript")
        assert len(result) == 1
        assert result[0]["technology"] == "JavaScript"

    def test_query_filters_by_name(self, server) -> None:
        result = server.list_tracks(query="python")
        assert len(result) == 2

    def test_no_match_returns_all(self, server) -> None:
        result = server.list_tracks(query="rust")
        assert len(result) == 3  # fallback

    def test_result_has_expected_keys(self, server) -> None:
        result = server.list_tracks()
        expected_keys = {"id", "name", "technology", "level", "modules", "total_xp", "lifetime"}
        assert set(result[0].keys()) == expected_keys


# ── get_track ─────────────────────────────────────────────────────────────────


class TestGetTrack:
    def test_returns_full_track(self, server) -> None:
        result = server.get_track(track_id=1)
        assert result["id"] == 1
        assert result["name"] == SAMPLE_TRACKS[0]["name"]
        assert "available_badges" in result

    def test_unknown_id_returns_error(self, server) -> None:
        result = server.get_track(track_id=999)
        assert "error" in result

    def test_all_fields_present(self, server) -> None:
        result = server.get_track(track_id=2)
        for key in ("id", "name", "technology", "level", "modules", "total_xp", "lifetime"):
            assert key in result


# ── get_progress ──────────────────────────────────────────────────────────────


class TestGetProgress:
    def test_empty_initially(self, server) -> None:
        result = server.get_progress()
        assert result == {"in_progress": [], "completed": []}

    def test_reflects_toggle(self, server) -> None:
        server.toggle_progress(track_id=1)
        result = server.get_progress()
        assert 1 in result["in_progress"]
        assert result["completed"] == []

    def test_reflects_complete(self, server) -> None:
        server.toggle_progress(track_id=1)
        server.complete_track(track_id=1)
        result = server.get_progress()
        assert result["in_progress"] == []
        assert 1 in result["completed"]


# ── toggle_progress ───────────────────────────────────────────────────────────


class TestToggleProgress:
    def test_starts_track(self, server) -> None:
        msg = server.toggle_progress(track_id=2)
        assert "andamento" in msg

    def test_removes_track(self, server) -> None:
        server.toggle_progress(track_id=2)
        msg = server.toggle_progress(track_id=2)
        assert "removida" in msg

    def test_completed_track_is_noop(self, server) -> None:
        server.toggle_progress(track_id=1)
        server.complete_track(track_id=1)
        msg = server.toggle_progress(track_id=1)
        assert "concluída" in msg


# ── generate_challenge ────────────────────────────────────────────────────────


class TestGenerateChallenge:
    def test_iniciante_challenge(self, server) -> None:
        text = server.generate_challenge(track_id=1)  # Python Iniciante
        assert "Python" in text
        assert "Maior" in text

    def test_intermediario_challenge(self, server) -> None:
        text = server.generate_challenge(track_id=2)  # JS Intermediário
        assert "JavaScript" in text

    def test_avancado_challenge(self, server) -> None:
        text = server.generate_challenge(track_id=3)  # Python Avançado
        assert "LRU" in text

    def test_unknown_track_returns_error_string(self, server) -> None:
        result = server.generate_challenge(track_id=999)
        assert "not found" in result


# ── complete_track ────────────────────────────────────────────────────────────


class TestCompleteTrack:
    def test_requires_in_progress(self, server) -> None:
        result = server.complete_track(track_id=1)
        assert "toggle_progress" in result

    def test_completes_in_progress_track(self, server) -> None:
        server.toggle_progress(track_id=1)
        result = server.complete_track(track_id=1)
        assert "concluída" in result.lower() or "Parabéns" in result
        progress = server.get_progress()
        assert 1 in progress["completed"]


# ── get_certificate ───────────────────────────────────────────────────────────


class TestGetCertificate:
    def test_requires_completed_track(self, server) -> None:
        result = server.get_certificate(track_id=1, username="Ana")
        assert "error" in result
        assert "completed" in result["error"].lower() or "not completed" in result["error"].lower()

    def test_requires_username_for_new_cert(self, server) -> None:
        server.toggle_progress(track_id=1)
        server.complete_track(track_id=1)
        result = server.get_certificate(track_id=1, username="")
        assert "error" in result
        assert "username" in result["error"].lower()

    def test_generates_certificate(self, server) -> None:
        server.toggle_progress(track_id=1)
        server.complete_track(track_id=1)
        result = server.get_certificate(track_id=1, username="Ana")
        assert "lines" in result
        assert result["from_cache"] is False
        assert isinstance(result["lines"], list)

    def test_loads_from_cache(self, server) -> None:
        server.toggle_progress(track_id=1)
        server.complete_track(track_id=1)
        server.get_certificate(track_id=1, username="Ana")
        result = server.get_certificate(track_id=1, username="Ana")
        assert result["from_cache"] is True

    def test_unknown_track_returns_error(self, server) -> None:
        result = server.get_certificate(track_id=999, username="Ana")
        assert "error" in result

    def test_certificate_contains_username(self, server) -> None:
        server.toggle_progress(track_id=1)
        server.complete_track(track_id=1)
        result = server.get_certificate(track_id=1, username="Beatriz")
        full = "\n".join(result["lines"])
        assert "BEATRIZ" in full
