"""Model layer — data types and repository. No curses dependency."""

import json
from typing import TypedDict


class Promotion(TypedDict):
    discount: str
    valid_until: str
    description: str


class Live(TypedDict):
    title: str
    date: str


class Trilha(TypedDict):
    id: int
    name: str
    technology: str
    level: str
    modules: int
    total_xp: int
    available_badges: list[str]
    promotions: Promotion
    lifetime: bool
    lives: list[Live]


class TrilhaRepository:
    def __init__(self, path: str) -> None:
        with open(path, encoding="utf-8") as f:
            self._data: list[Trilha] = json.load(f)["trilhas"]

    def all(self) -> list[Trilha]:
        return self._data


class ProgressRepository:
    def __init__(self, path: str) -> None:
        self._path = path
        raw = self._load_raw()
        self._in_progress: set[int] = set(raw.get("in_progress", []))
        self._completed: set[int] = set(raw.get("completed", []))

    def _load_raw(self) -> dict:
        try:
            with open(self._path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "in_progress": sorted(self._in_progress),
                    "completed": sorted(self._completed),
                },
                f,
                indent=2,
            )

    # ── in_progress ──
    def all_ids(self) -> set[int]:
        return set(self._in_progress)

    def is_in_progress(self, trilha_id: int) -> bool:
        return trilha_id in self._in_progress

    def add(self, trilha_id: int) -> None:
        self._in_progress.add(trilha_id)
        self._save()

    def remove(self, trilha_id: int) -> None:
        self._in_progress.discard(trilha_id)
        self._save()

    # ── completed ──
    def all_completed_ids(self) -> set[int]:
        return set(self._completed)

    def is_completed(self, trilha_id: int) -> bool:
        return trilha_id in self._completed

    def complete(self, trilha_id: int) -> None:
        """Move a trilha from in_progress to completed (irreversible)."""
        self._in_progress.discard(trilha_id)
        self._completed.add(trilha_id)
        self._save()
