"""Tests for service.py — TrackService, ProgressService, ChallengeService, CertificateService."""

from pathlib import Path

from conftest import SAMPLE_TRACKS
from model import ProgressRepository, TrackRepository
from service import (
    CertificateService,
    ChallengeService,
    ProgressService,
    TrackService,
)

# ── helpers ───────────────────────────────────────────────────────────────────


def make_track_service(tracks_json: Path) -> TrackService:
    return TrackService(TrackRepository(str(tracks_json)))


def make_progress_service(progress_json: Path) -> ProgressService:
    return ProgressService(ProgressRepository(str(progress_json)))


# ── TrackService ──────────────────────────────────────────────────────────────


class TestTrackService:
    def test_all_returns_all(self, tracks_json: Path) -> None:
        svc = make_track_service(tracks_json)
        assert len(svc.all()) == 3

    def test_search_empty_query_returns_all(self, tracks_json: Path) -> None:
        svc = make_track_service(tracks_json)
        result = svc.search("")
        assert result.found is True
        assert len(result.tracks) == 3
        assert result.message == ""

    def test_search_by_name(self, tracks_json: Path) -> None:
        svc = make_track_service(tracks_json)
        result = svc.search("python")
        assert result.found is True
        # tracks 1 and 3 mention python in name or technology
        ids = {t["id"] for t in result.tracks}
        assert 1 in ids
        assert 3 in ids

    def test_search_by_technology(self, tracks_json: Path) -> None:
        svc = make_track_service(tracks_json)
        result = svc.search("javascript")
        assert result.found is True
        assert len(result.tracks) == 1
        assert result.tracks[0]["id"] == 2

    def test_search_no_match_returns_all(self, tracks_json: Path) -> None:
        svc = make_track_service(tracks_json)
        result = svc.search("rust")
        assert result.found is False
        assert len(result.tracks) == 3  # fallback: all
        assert "Nenhuma" in result.message

    def test_search_case_insensitive(self, tracks_json: Path) -> None:
        svc = make_track_service(tracks_json)
        result = svc.search("PYTHON")
        assert result.found is True
        assert any(t["technology"] == "Python" for t in result.tracks)


# ── ProgressService ───────────────────────────────────────────────────────────


class TestProgressService:
    def test_toggle_starts_track(self, progress_json: Path) -> None:
        svc = make_progress_service(progress_json)
        msg = svc.toggle(1)
        assert svc.is_in_progress(1)
        assert "andamento" in msg

    def test_toggle_removes_track(self, progress_json: Path) -> None:
        svc = make_progress_service(progress_json)
        svc.toggle(1)
        msg = svc.toggle(1)
        assert not svc.is_in_progress(1)
        assert "removida" in msg

    def test_toggle_on_completed_is_noop(self, progress_json: Path) -> None:
        svc = make_progress_service(progress_json)
        svc.toggle(1)
        svc.complete(1)
        msg = svc.toggle(1)
        assert "concluída" in msg
        assert svc.is_in_progress(1) is False

    def test_complete_returns_message(self, progress_json: Path) -> None:
        svc = make_progress_service(progress_json)
        svc.toggle(1)
        msg = svc.complete(1)
        assert "concluída" in msg.lower() or "Parabéns" in msg

    def test_all_ids_and_completed_ids(self, progress_json: Path) -> None:
        svc = make_progress_service(progress_json)
        svc.toggle(1)
        svc.toggle(2)
        svc.complete(1)
        assert svc.all_ids() == {2}
        assert svc.all_completed_ids() == {1}


# ── ChallengeService ──────────────────────────────────────────────────────────


class TestChallengeService:
    def test_iniciante_challenge(self) -> None:
        svc = ChallengeService()
        track = SAMPLE_TRACKS[0]  # level: Iniciante, technology: Python
        text = svc.generate(track)  # type: ignore[arg-type]
        assert "Python" in text
        assert "Maior" in text

    def test_intermediario_challenge(self) -> None:
        svc = ChallengeService()
        track = SAMPLE_TRACKS[1]  # level: Intermediário, technology: JavaScript
        text = svc.generate(track)  # type: ignore[arg-type]
        assert "JavaScript" in text
        assert "frequência" in text or "dicionário" in text

    def test_avancado_challenge(self) -> None:
        svc = ChallengeService()
        track = SAMPLE_TRACKS[2]  # level: Avançado, technology: Python
        text = svc.generate(track)  # type: ignore[arg-type]
        assert "Python" in text
        assert "LRU" in text

    def test_unknown_level_falls_back_to_iniciante(self) -> None:
        svc = ChallengeService()
        track = {**SAMPLE_TRACKS[0], "level": "Desconhecido"}
        text = svc.generate(track)  # type: ignore[arg-type]
        assert "Maior" in text  # iniciante template


# ── CertificateService ────────────────────────────────────────────────────────


class TestCertificateService:
    def test_load_returns_none_when_missing(self, certs_dir: Path) -> None:
        svc = CertificateService(str(certs_dir))
        assert svc.load(1) is None

    def test_generate_returns_lines(self, certs_dir: Path) -> None:
        svc = CertificateService(str(certs_dir))
        track = SAMPLE_TRACKS[0]
        lines = svc.generate(track, "João Silva")  # type: ignore[arg-type]
        assert isinstance(lines, list)
        assert len(lines) > 0

    def test_generate_contains_username(self, certs_dir: Path) -> None:
        svc = CertificateService(str(certs_dir))
        track = SAMPLE_TRACKS[0]
        lines = svc.generate(track, "Maria")  # type: ignore[arg-type]
        full = "\n".join(lines)
        assert "MARIA" in full

    def test_generate_persists_and_load_returns_it(self, certs_dir: Path) -> None:
        svc = CertificateService(str(certs_dir))
        track = SAMPLE_TRACKS[0]
        generated = svc.generate(track, "Ana")  # type: ignore[arg-type]
        loaded = svc.load(track["id"])
        assert loaded == generated

    def test_generate_creates_dir(self, tmp_path: Path) -> None:
        nested = tmp_path / "deep" / "certs"
        CertificateService(str(nested))
        assert nested.exists()

    def test_certificate_contains_track_name(self, certs_dir: Path) -> None:
        svc = CertificateService(str(certs_dir))
        track = SAMPLE_TRACKS[0]
        lines = svc.generate(track, "Test")  # type: ignore[arg-type]
        full = "\n".join(lines)
        assert track["name"] in full

    def test_certificate_contains_verification_code(self, certs_dir: Path) -> None:
        svc = CertificateService(str(certs_dir))
        track = SAMPLE_TRACKS[0]
        lines = svc.generate(track, "Test")  # type: ignore[arg-type]
        full = "\n".join(lines)
        assert "DIO-" in full
