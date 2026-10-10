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
        self._data: set[int] = self._load()

    def _load(self) -> set[int]:
        try:
            with open(self._path, encoding="utf-8") as f:
                return set(json.load(f).get("in_progress", []))
        except FileNotFoundError:
            return set()

    def _save(self) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump({"in_progress": sorted(self._data)}, f, indent=2)

    def all_ids(self) -> set[int]:
        return set(self._data)

    def is_in_progress(self, trilha_id: int) -> bool:
        return trilha_id in self._data

    def add(self, trilha_id: int) -> None:
        self._data.add(trilha_id)
        self._save()

    def remove(self, trilha_id: int) -> None:
        self._data.discard(trilha_id)
        self._save()
