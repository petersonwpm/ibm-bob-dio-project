"""Tests for model.py — TrackRepository and ProgressRepository."""

import json
from pathlib import Path

import pytest
from model import ProgressRepository, TrackRepository

# ── TrackRepository ───────────────────────────────────────────────────────────


class TestTrackRepository:
    def test_loads_all_tracks(self, tracks_json: Path) -> None:
        repo = TrackRepository(str(tracks_json))
        assert len(repo.all()) == 3

    def test_track_fields(self, tracks_json: Path) -> None:
        repo = TrackRepository(str(tracks_json))
        first = repo.all()[0]
        assert first["id"] == 1
        assert first["name"] == "Fundamentos de Python para Iniciantes"
        assert first["technology"] == "Python"
        assert first["level"] == "Iniciante"

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            TrackRepository(str(tmp_path / "nonexistent.json"))


# ── ProgressRepository ────────────────────────────────────────────────────────


class TestProgressRepository:
    def test_empty_when_file_missing(self, progress_json: Path) -> None:
        repo = ProgressRepository(str(progress_json))
        assert repo.all_ids() == set()
        assert repo.all_completed_ids() == set()

    def test_add_persists(self, progress_json: Path) -> None:
        repo = ProgressRepository(str(progress_json))
        repo.add(1)
        assert repo.is_in_progress(1)
        # Reload from disk to verify persistence
        repo2 = ProgressRepository(str(progress_json))
        assert repo2.is_in_progress(1)

    def test_remove(self, progress_json: Path) -> None:
        repo = ProgressRepository(str(progress_json))
        repo.add(1)
        repo.remove(1)
        assert not repo.is_in_progress(1)

    def test_remove_nonexistent_is_safe(self, progress_json: Path) -> None:
        repo = ProgressRepository(str(progress_json))
        repo.remove(99)  # must not raise
        assert repo.all_ids() == set()

    def test_complete_moves_from_in_progress(self, progress_json: Path) -> None:
        repo = ProgressRepository(str(progress_json))
        repo.add(1)
        repo.complete(1)
        assert not repo.is_in_progress(1)
        assert repo.is_completed(1)

    def test_complete_without_prior_add(self, progress_json: Path) -> None:
        repo = ProgressRepository(str(progress_json))
        repo.complete(2)
        assert repo.is_completed(2)
        assert not repo.is_in_progress(2)

    def test_all_ids_returns_copy(self, progress_json: Path) -> None:
        repo = ProgressRepository(str(progress_json))
        repo.add(1)
        ids = repo.all_ids()
        ids.add(99)
        assert 99 not in repo.all_ids()

    def test_loads_existing_file(self, tmp_path: Path) -> None:
        p = tmp_path / "progress.json"
        p.write_text(json.dumps({"in_progress": [2, 3], "completed": [1]}), encoding="utf-8")
        repo = ProgressRepository(str(p))
        assert repo.all_ids() == {2, 3}
        assert repo.all_completed_ids() == {1}
